from django.db import transaction
from django.db.models import F

from catalog.models import ProductVariant

from .models import Order, OrderItem


class OutOfStockError(Exception):
    pass


@transaction.atomic
def place_order(user, order_form, cart_lines):
    if not cart_lines:
        raise ValueError('Корзина пуста.')
    variants = ProductVariant.objects.select_for_update().select_related('product').in_bulk(
        [line.variant.pk for line in cart_lines]
    )
    order = order_form.save(commit=False)
    order.user = user
    order.save()
    for line in cart_lines:
        variant = variants.get(line.variant.pk)
        if variant is None or not variant.product.is_active:
            raise OutOfStockError('Один из товаров больше недоступен.')
        if line.quantity < 1 or ProductVariant.objects.filter(pk=variant.pk, stock__gte=line.quantity).update(
            stock=F('stock') - line.quantity,
        ) != 1:
            raise OutOfStockError(
                f'Товара «{variant.product.name}» размера {variant.size} на складе {variant.stock} шт., а в корзине {line.quantity}.'
            )
        OrderItem.objects.create(order=order, variant=variant, product_name=variant.product.name,
                                 size=variant.size, price=variant.product.price, quantity=line.quantity)
    return order


@transaction.atomic
def cancel_order(order):
    current = Order.objects.select_for_update().get(pk=order.pk)
    if current.status not in (Order.Status.NEW, Order.Status.CONFIRMED):
        return False
    for item in current.items.all():
        ProductVariant.objects.filter(pk=item.variant_id).update(stock=F('stock') + item.quantity)
    current.status = Order.Status.CANCELLED
    current.save(update_fields=['status', 'updated_at'])
    order.status = current.status
    return True
