from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from catalog.models import Brand, Category, Product, ProductVariant

from .models import Order
from .services import cancel_order

ORDER_DATA = {'full_name': 'Анна Смирнова', 'phone': '+7 913 000-00-00', 'address': 'Новосибирск'}


class SportsOrderTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name='Бег', slug='running')
        brand = Brand.objects.create(name='Runway', slug='runway')
        cls.product = Product.objects.create(category=category, brand=brand, name='Кроссовки',
                                             slug='shoes', price=Decimal('5000'))
        cls.size40 = ProductVariant.objects.create(product=cls.product, size='40', stock=5)
        cls.size41 = ProductVariant.objects.create(product=cls.product, size='41', stock=3)
        cls.buyer = User.objects.create_user('anna', password='test-pass-123')
        cls.other = User.objects.create_user('boris', password='test-pass-123')

    def add(self, variant, quantity):
        return self.client.post(reverse('cart:add', args=[variant.pk]), {'quantity': quantity})

    def test_cart_separates_sizes(self):
        self.add(self.size40, 2)
        self.add(self.size41, 1)
        self.assertEqual(self.client.session['cart'], {str(self.size40.pk): 2, str(self.size41.pk): 1})

    def test_checkout_requires_login(self):
        self.add(self.size40, 1)
        response = self.client.get(reverse('orders:checkout'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('orders:checkout')}")

    def test_checkout_decrements_only_selected_size(self):
        self.client.force_login(self.buyer)
        self.add(self.size40, 2)
        self.client.post(reverse('orders:checkout'), ORDER_DATA)
        self.size40.refresh_from_db()
        self.size41.refresh_from_db()
        self.assertEqual(self.size40.stock, 3)
        self.assertEqual(self.size41.stock, 3)
        item = Order.objects.get().items.get()
        self.assertEqual((item.size, item.price), ('40', Decimal('5000')))

    def test_failed_second_size_rolls_back_first(self):
        self.client.force_login(self.buyer)
        self.add(self.size40, 2)
        self.add(self.size41, 2)
        ProductVariant.objects.filter(pk=self.size41.pk).update(stock=1)
        response = self.client.post(reverse('orders:checkout'), ORDER_DATA)
        self.assertRedirects(response, reverse('cart:detail'))
        self.assertFalse(Order.objects.exists())
        self.size40.refresh_from_db()
        self.assertEqual(self.size40.stock, 5)
        self.assertEqual(len(self.client.session['cart']), 2)

    def test_cancel_restores_each_size_once(self):
        self.client.force_login(self.buyer)
        self.add(self.size40, 2)
        self.client.post(reverse('orders:checkout'), ORDER_DATA)
        order = Order.objects.get()
        self.assertTrue(cancel_order(order))
        self.assertFalse(cancel_order(order))
        self.size40.refresh_from_db()
        self.assertEqual(self.size40.stock, 5)

    def test_foreign_order_is_404(self):
        order = Order.objects.create(user=self.buyer, **ORDER_DATA)
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(order.get_absolute_url()).status_code, 404)

    def test_price_snapshot(self):
        self.client.force_login(self.buyer)
        self.add(self.size40, 1)
        self.client.post(reverse('orders:checkout'), ORDER_DATA)
        Product.objects.filter(pk=self.product.pk).update(price=Decimal('9000'))
        self.assertEqual(Order.objects.get().items.get().price, Decimal('5000'))
