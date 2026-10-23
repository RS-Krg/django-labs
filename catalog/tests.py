from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import Brand, Category, Product, ProductVariant


class SportsCatalogTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name='Бег', slug='running')
        cls.brand = Brand.objects.create(name='Runway', slug='runway')
        cls.product = Product.objects.create(category=cls.category, brand=cls.brand,
                                             name='Кроссовки Бег', slug='running-shoes', price=Decimal('5000'))
        cls.size40 = ProductVariant.objects.create(product=cls.product, size='40', stock=2)
        cls.size41 = ProductVariant.objects.create(product=cls.product, size='41', stock=0)

    def test_brand_filter(self):
        response = self.client.get(reverse('catalog:product_list'), {'brand': 'runway'})
        self.assertContains(response, self.product.name)
        response = self.client.get(reverse('catalog:product_list'), {'brand': 'other'})
        self.assertNotContains(response, self.product.name)

    def test_size_filter_requires_available_variant(self):
        response = self.client.get(reverse('catalog:product_list'), {'size': '40'})
        self.assertContains(response, self.product.name)
        response = self.client.get(reverse('catalog:product_list'), {'size': '41'})
        self.assertNotContains(response, self.product.name)

    def test_out_of_stock_product_is_visible_but_not_buyable(self):
        ProductVariant.objects.filter(product=self.product).update(stock=0)
        response = self.client.get(self.product.get_absolute_url())
        self.assertContains(response, 'Нет в наличии')
        self.assertNotContains(response, 'В корзину')

    def test_cyrillic_search_ignores_case(self):
        response = self.client.get(reverse('catalog:product_list'), {'q': 'КРОССОВКИ'})
        self.assertContains(response, self.product.name)

    def test_pagination(self):
        for i in range(9):
            Product.objects.create(category=self.category, brand=self.brand,
                                   name=f'Майка {i}', slug=f'shirt-{i}', price=Decimal('1000'))
        response = self.client.get(reverse('catalog:product_list'), {'page': 2})
        self.assertEqual(response.context['page'].number, 2)

    def test_cannot_add_empty_size(self):
        response = self.client.post(reverse('cart:add', args=[self.size41.pk]), {'quantity': 1})
        self.assertRedirects(response, reverse('cart:detail'))
        self.assertEqual(self.client.session['cart'], {})
