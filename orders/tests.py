from decimal import Decimal
from unittest.mock import Mock

from django.contrib import admin
from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from catalog.models import Category, Product

from .models import Order
from .admin import OrderAdmin
from .services import cancel_order

ORDER_DATA = {'full_name': 'Анна Смирнова', 'phone': '+7 913 000-00-00', 'address': 'Новосибирск'}


class CheckoutTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name='Мониторы', slug='monitors')
        cls.product = Product.objects.create(category=category, name='Монитор', slug='monitor',
                                             price=Decimal('10000'), stock=5)
        cls.buyer = User.objects.create_user('anna', password='test-pass-123')
        cls.other = User.objects.create_user('boris', password='test-pass-123')

    def add_to_cart(self, quantity):
        return self.client.post(reverse('cart:add', args=[self.product.pk]), {'quantity': quantity})

    def test_cart_quantity_is_limited_by_stock(self):
        self.add_to_cart(3)
        self.add_to_cart(3)
        self.assertEqual(self.client.session['cart'], {str(self.product.pk): 5})

    def test_checkout_requires_login(self):
        self.add_to_cart(1)
        response = self.client.get(reverse('orders:checkout'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('orders:checkout')}")

    def test_checkout_creates_order_and_decreases_stock(self):
        self.client.force_login(self.buyer)
        self.add_to_cart(2)
        response = self.client.post(reverse('orders:checkout'), ORDER_DATA)
        order = Order.objects.get(user=self.buyer)
        self.assertRedirects(response, order.get_absolute_url())
        self.assertEqual(order.total_price, Decimal('20000'))
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)
        self.assertEqual(self.client.session['cart'], {})

    def test_order_keeps_price_at_purchase_time(self):
        self.client.force_login(self.buyer)
        self.add_to_cart(1)
        self.client.post(reverse('orders:checkout'), ORDER_DATA)
        Product.objects.filter(pk=self.product.pk).update(price=Decimal('15000'))
        self.assertEqual(Order.objects.get(user=self.buyer).items.get().price, Decimal('10000'))

    def test_out_of_stock_rolls_back_everything(self):
        self.client.force_login(self.buyer)
        self.add_to_cart(4)
        Product.objects.filter(pk=self.product.pk).update(stock=2)
        response = self.client.post(reverse('orders:checkout'), ORDER_DATA)
        self.assertRedirects(response, reverse('cart:detail'))
        self.assertFalse(Order.objects.exists())
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 2)

    def test_cancel_returns_stock(self):
        self.client.force_login(self.buyer)
        self.add_to_cart(2)
        self.client.post(reverse('orders:checkout'), ORDER_DATA)
        order = Order.objects.get(user=self.buyer)
        self.client.post(reverse('orders:cancel', args=[order.pk]))
        order.refresh_from_db()
        self.product.refresh_from_db()
        self.assertEqual(order.status, Order.Status.CANCELLED)
        self.assertEqual(self.product.stock, 5)

    def test_foreign_order_is_not_visible(self):
        order = Order.objects.create(user=self.buyer, **ORDER_DATA)
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(order.get_absolute_url()).status_code, 404)

    def test_double_cancel_does_not_double_restock(self):
        self.client.force_login(self.buyer)
        self.add_to_cart(2)
        self.client.post(reverse('orders:checkout'), ORDER_DATA)
        order = Order.objects.get(user=self.buyer)
        self.assertTrue(cancel_order(order))
        self.assertFalse(cancel_order(order))
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 5)

    def test_manager_cannot_skip_status_transition(self):
        order = Order.objects.create(user=self.buyer, **ORDER_DATA)
        order_admin = OrderAdmin(Order, admin.site)
        order_admin.message_user = Mock()
        order_admin.mark_done(None, Order.objects.filter(pk=order.pk))
        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.NEW)
