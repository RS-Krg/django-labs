from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from catalog.models import Product

from .cart import Cart
from .forms import CartAddForm


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    form = CartAddForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'Укажите количество от 1 до 99.')
        return redirect(product)
    cart = Cart(request)
    quantity = form.cleaned_data['quantity']
    replace = form.cleaned_data['replace']
    requested = quantity if replace else cart.get_quantity(product) + quantity
    in_cart = cart.add(product, quantity, replace=replace)
    if in_cart == 0:
        messages.error(request, f'Товара «{product.name}» нет в наличии.')
    elif in_cart < requested:
        messages.warning(request, f'На складе только {product.stock} шт. товара «{product.name}».')
    else:
        messages.success(request, f'«{product.name}»: в корзине {in_cart} шт.')
    return redirect('cart:detail')


@require_POST
def cart_remove(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    Cart(request).remove(product)
    messages.info(request, f'«{product.name}» удалён из корзины.')
    return redirect('cart:detail')


def cart_detail(request):
    lines = Cart(request).lines()
    return render(request, 'cart/detail.html', {
        'lines': lines, 'total': sum((line.total for line in lines), 0),
    })
