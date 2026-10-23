from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from cart.cart import Cart

from .forms import OrderForm
from .services import OutOfStockError, cancel_order, place_order


@login_required
def checkout(request):
    cart = Cart(request)
    lines = cart.lines()
    if not lines:
        messages.info(request, 'Корзина пуста.')
        return redirect('cart:detail')
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            try:
                order = place_order(request.user, form, lines)
            except OutOfStockError as error:
                messages.error(request, str(error))
                return redirect('cart:detail')
            cart.clear()
            messages.success(request, f'Заказ №{order.pk} оформлен. Спасибо за покупку!')
            return redirect(order)
    else:
        form = OrderForm(initial={'full_name': request.user.get_full_name()})
    return render(request, 'orders/checkout.html', {
        'form': form, 'lines': lines, 'total': sum(line.total for line in lines),
    })


@login_required
def order_list(request):
    return render(request, 'orders/order_list.html', {
        'orders': request.user.orders.prefetch_related('items'),
    })


@login_required
def order_detail(request, pk):
    order = get_object_or_404(request.user.orders.prefetch_related('items__variant__product'), pk=pk)
    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
@require_POST
def order_cancel(request, pk):
    order = get_object_or_404(request.user.orders, pk=pk)
    if order.can_be_cancelled and cancel_order(order):
        messages.success(request, f'Заказ №{order.pk} отменён, товары возвращены на склад.')
    else:
        messages.error(request, f'Заказ в статусе «{order.get_status_display()}» отменить нельзя.')
    return redirect(order)
