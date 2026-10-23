from django.db import transaction
from django.db.models import F

from catalog.models import Product

from .models import Order, OrderItem


class OutOfStockError(Exception):
    pass


@transaction.atomic
def place_order(user, order_form, cart_lines):
    if not cart_lines:
        raise ValueError('Корзина пуста.')
    products = Product.objects.select_for_update().in_bulk([line.product.pk for line in cart_lines])
    order = order_form.save(commit=False)
    order.user = user
    order.save()
    for line in cart_lines:
        product = products.get(line.product.pk)
        if product is None or not product.is_active:
            raise OutOfStockError('Один из товаров больше недоступен.')
        if line.quantity < 1 or Product.objects.filter(pk=product.pk, stock__gte=line.quantity).update(
            stock=F('stock') - line.quantity,
        ) != 1:
            raise OutOfStockError(
                f'Товара «{product.name}» на складе {product.stock} шт., а в корзине {line.quantity}.'
            )
        OrderItem.objects.create(order=order, product=product, price=product.price, quantity=line.quantity)
    return order


@transaction.atomic
def cancel_order(order):
    current = Order.objects.select_for_update().get(pk=order.pk)
    if current.status not in (Order.Status.NEW, Order.Status.CONFIRMED):
        return False
    for item in current.items.all():
        Product.objects.filter(pk=item.product_id).update(stock=F('stock') + item.quantity)
    current.status = Order.Status.CANCELLED
    current.save(update_fields=['status', 'updated_at'])
    order.status = current.status
    return True
