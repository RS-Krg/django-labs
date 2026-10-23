from decimal import Decimal

from django.conf import settings
from django.db import models
from django.urls import reverse

from catalog.models import Product


class Order(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'Новый'
        CONFIRMED = 'confirmed', 'Подтверждён'
        SHIPPED = 'shipped', 'Передан в доставку'
        DONE = 'done', 'Выполнен'
        CANCELLED = 'cancelled', 'Отменён'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Покупатель',
                             on_delete=models.PROTECT, related_name='orders')
    status = models.CharField('Статус', max_length=20, choices=Status.choices, default=Status.NEW)
    full_name = models.CharField('Получатель', max_length=150)
    phone = models.CharField('Телефон', max_length=30)
    address = models.CharField('Адрес доставки', max_length=300)
    comment = models.TextField('Комментарий', blank=True)
    created_at = models.DateTimeField('Оформлен', auto_now_add=True)
    updated_at = models.DateTimeField('Изменён', auto_now=True)

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заказ №{self.pk}'

    def get_absolute_url(self):
        return reverse('orders:detail', args=[self.pk])

    @property
    def total_price(self):
        return sum((item.total for item in self.items.all()), Decimal('0'))

    @property
    def can_be_cancelled(self):
        return self.status == self.Status.NEW


class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name='Заказ', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, verbose_name='Товар', on_delete=models.PROTECT,
                                related_name='order_items')
    price = models.DecimalField('Цена на момент заказа', max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField('Количество')

    class Meta:
        verbose_name = 'позиция заказа'
        verbose_name_plural = 'позиции заказа'
        constraints = [models.CheckConstraint(condition=models.Q(quantity__gt=0), name='shop_order_item_qty_positive')]

    def __str__(self):
        return f'{self.product} × {self.quantity}'

    @property
    def total(self):
        return self.price * self.quantity
