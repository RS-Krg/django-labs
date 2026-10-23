from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import Category, Product


class CatalogTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.monitors = Category.objects.create(name='Мониторы', slug='monitors')
        cls.storage = Category.objects.create(name='Накопители', slug='storage')
        cls.monitor = Product.objects.create(category=cls.monitors, name='Монитор 27 дюймов',
                                             slug='monitor-27', price=Decimal('21990'), stock=5)
        cls.ssd = Product.objects.create(category=cls.storage, name='SSD 1 ТБ',
                                         slug='ssd-1tb', price=Decimal('7490'), stock=0)
        cls.hidden = Product.objects.create(category=cls.monitors, name='Снятый с продажи монитор',
                                            slug='hidden', price=Decimal('1000'), is_active=False)

    def test_inactive_product_is_hidden(self):
        response = self.client.get(reverse('catalog:product_list'))
        self.assertContains(response, self.monitor.name)
        self.assertNotContains(response, self.hidden.name)
        self.assertEqual(self.client.get(self.hidden.get_absolute_url()).status_code, 404)

    def test_category_filter(self):
        response = self.client.get(self.storage.get_absolute_url())
        self.assertContains(response, self.ssd.name)
        self.assertNotContains(response, self.monitor.name)

    def test_search_ignores_case(self):
        response = self.client.get(reverse('catalog:product_list'), {'q': 'МОНИТОР'})
        self.assertContains(response, self.monitor.name)
        self.assertNotContains(response, self.ssd.name)

    def test_product_page_shows_stock(self):
        self.assertContains(self.client.get(self.ssd.get_absolute_url()), 'Нет в наличии')

    def test_pagination(self):
        for number in range(10):
            Product.objects.create(category=self.storage, name=f'Флешка {number}',
                                   slug=f'flash-{number}', price=Decimal('500'))
        response = self.client.get(reverse('catalog:product_list'), {'page': 2})
        self.assertEqual(response.context['page'].number, 2)

    def test_bad_sort_is_safe(self):
        response = self.client.get(reverse('catalog:product_list'), {'sort': 'password'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['sort'], 'name')
