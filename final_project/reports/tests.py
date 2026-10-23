from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from catalog.models import Brand, Category, Product, ProductVariant
from orders.models import Order, OrderItem


class ReportTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.buyer = User.objects.create_user('buyer', password='pass-12345')
        cls.manager = User.objects.create_user('manager', password='pass-12345', is_staff=True)
        group = Group.objects.create(name='Менеджеры')
        cls.manager.groups.add(group)
        category = Category.objects.create(name='Бег', slug='running')
        brand = Brand.objects.create(name='Runway', slug='runway')
        product = Product.objects.create(category=category, brand=brand, name='Кроссовки',
                                         slug='shoes', price=Decimal('1000'))
        variant = ProductVariant.objects.create(product=product, size='40', stock=5)
        for status in (Order.Status.DONE, Order.Status.CANCELLED):
            order = Order.objects.create(user=cls.buyer, status=status, full_name='Покупатель',
                                         phone='123', address='Адрес')
            OrderItem.objects.create(order=order, variant=variant, product_name=product.name,
                                     size='40', price=Decimal('1000'), quantity=2)

    def test_buyer_forbidden(self):
        self.client.force_login(self.buyer)
        self.assertEqual(self.client.get(reverse('reports:index')).status_code, 403)

    def test_manager_report_excludes_cancelled_revenue(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse('reports:index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total'], Decimal('2000'))
        self.assertEqual(sum(row['count'] for row in response.context['statuses']), 2)

    def test_period_validation(self):
        self.client.force_login(self.manager)
        today = timezone.localdate()
        response = self.client.get(reverse('reports:index'), {
            'date_from': today + timedelta(days=1), 'date_to': today,
        })
        self.assertContains(response, 'Дата начала должна быть не позже даты окончания.')

    def test_csv(self):
        self.client.force_login(self.manager)
        today = timezone.localdate().isoformat()
        response = self.client.get(reverse('reports:index'), {
            'date_from': today, 'date_to': today, 'format': 'csv',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/csv', response['Content-Type'])
        self.assertIn('2000', response.content.decode('utf-8'))
