from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField('Название', max_length=100, unique=True)
    slug = models.SlugField('Адрес (slug)', max_length=100, unique=True)
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:product_list_by_category', args=[self.slug])


class Brand(models.Model):
    name = models.CharField('Бренд', max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name = 'бренд'
        verbose_name_plural = 'бренды'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.PROTECT,
                                 related_name='products')
    brand = models.ForeignKey(Brand, verbose_name='Бренд', on_delete=models.PROTECT,
                              related_name='products')
    name = models.CharField('Название', max_length=200)
    slug = models.SlugField('Адрес (slug)', max_length=200, unique=True)
    description = models.TextField('Описание', blank=True)
    price = models.DecimalField('Цена, ₽', max_digits=10, decimal_places=2,
                                validators=[MinValueValidator(Decimal('0.01'))])
    image = models.ImageField('Фото', upload_to='products/', blank=True)
    is_active = models.BooleanField('Показывать в каталоге', default=True)
    search_index = models.TextField(editable=False, blank=True)
    created_at = models.DateTimeField('Добавлен', auto_now_add=True)
    updated_at = models.DateTimeField('Изменён', auto_now=True)

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'
        ordering = ['name']
        constraints = [models.CheckConstraint(condition=models.Q(price__gt=0), name='product_price_positive')]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.search_index = f'{self.name} {self.description}'.lower()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('catalog:product_detail', args=[self.slug])

    @property
    def in_stock(self):
        return self.variants.filter(stock__gt=0).exists()


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, verbose_name='Товар', on_delete=models.CASCADE,
                                related_name='variants')
    size = models.CharField('Размер', max_length=20)
    stock = models.PositiveIntegerField('Остаток размера', default=0)

    class Meta:
        verbose_name = 'вариант товара'
        verbose_name_plural = 'варианты товара'
        constraints = [
            models.UniqueConstraint(fields=['product', 'size'], name='unique_product_size'),
            models.CheckConstraint(condition=models.Q(stock__gte=0), name='variant_stock_nonnegative'),
        ]

    def __str__(self):
        return f'{self.product.name} — {self.size}'
