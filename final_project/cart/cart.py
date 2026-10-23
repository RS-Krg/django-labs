from dataclasses import dataclass
from decimal import Decimal

from catalog.models import ProductVariant

CART_SESSION_KEY = 'cart'


@dataclass
class CartLine:
    variant: ProductVariant
    quantity: int

    @property
    def product(self):
        return self.variant.product

    @property
    def total(self):
        return self.variant.product.price * self.quantity


class Cart:
    def __init__(self, request):
        self.session = request.session
        self.items = self.session.get(CART_SESSION_KEY, {})

    def get_quantity(self, variant):
        return self.items.get(str(variant.pk), 0)

    def add(self, variant, quantity=1, replace=False):
        key = str(variant.pk)
        if not replace:
            quantity += self.get_quantity(variant)
        quantity = min(quantity, variant.stock)
        if quantity > 0:
            self.items[key] = quantity
        else:
            self.items.pop(key, None)
        self.save()
        return quantity

    def remove(self, variant):
        self.items.pop(str(variant.pk), None)
        self.save()

    def clear(self):
        self.items = {}
        self.save()

    def save(self):
        self.session[CART_SESSION_KEY] = self.items
        self.session.modified = True

    def lines(self):
        variants = ProductVariant.objects.filter(
            pk__in=self.items.keys(), product__is_active=True,
        ).select_related('product')
        return [CartLine(variant, self.items[str(variant.pk)]) for variant in variants]

    def total_price(self):
        return sum((line.total for line in self.lines()), Decimal('0'))

    def __len__(self):
        return sum(self.items.values())
