import csv
from decimal import Decimal

from django.core.exceptions import PermissionDenied
from django.db.models import Count, DecimalField, ExpressionWrapper, F, Sum
from django.db.models.functions import TruncDate
from django.http import HttpResponse
from django.shortcuts import render

from orders.models import Order, OrderItem

from .forms import ReportPeriodForm


def report_data(start, end):
    orders = Order.objects.filter(created_at__date__range=(start, end))
    active_items = OrderItem.objects.filter(
        order__created_at__date__range=(start, end),
    ).exclude(order__status=Order.Status.CANCELLED)
    revenue_expr = ExpressionWrapper(F('price') * F('quantity'),
                                     output_field=DecimalField(max_digits=18, decimal_places=2))
    daily = active_items.annotate(day=TruncDate('order__created_at')).values('day').annotate(
        revenue=Sum(revenue_expr),
    ).order_by('day')
    statuses = orders.values('status').annotate(count=Count('id')).order_by('status')
    top = active_items.values('variant__product_id', 'product_name').annotate(
        revenue=Sum(revenue_expr), quantity=Sum('quantity'),
    ).order_by('-revenue')[:10]
    total = active_items.aggregate(revenue=Sum(revenue_expr))['revenue'] or Decimal('0')
    return daily, statuses, top, total


def index(request):
    if not request.user.is_authenticated:
        raise PermissionDenied
    if not (request.user.is_superuser or request.user.groups.filter(name='Менеджеры').exists()):
        raise PermissionDenied
    form = ReportPeriodForm(request.GET) if request.GET else ReportPeriodForm()
    daily = statuses = top = ()
    total = Decimal('0')
    if not request.GET or form.is_valid():
        start = form.cleaned_data['date_from'] if request.GET else form.initial['date_from']
        end = form.cleaned_data['date_to'] if request.GET else form.initial['date_to']
        daily, statuses, top, total = report_data(start, end)
        if request.GET.get('format') == 'csv':
            response = HttpResponse(content_type='text/csv; charset=utf-8')
            response['Content-Disposition'] = 'attachment; filename="reports.csv"'
            response.write('\ufeff')
            writer = csv.writer(response)
            writer.writerow(['Период', start, end])
            writer.writerow(['Выручка всего', total])
            writer.writerow(['Дата', 'Выручка'])
            for row in daily:
                writer.writerow([row['day'], row['revenue']])
            writer.writerow(['Статус', 'Заказов'])
            for row in statuses:
                writer.writerow([row['status'], row['count']])
            writer.writerow(['Товар', 'Штук', 'Выручка'])
            for row in top:
                writer.writerow([row['product_name'], row['quantity'], row['revenue']])
            return response
    return render(request, 'reports/index.html', {
        'form': form, 'daily': daily, 'statuses': statuses, 'top': top, 'total': total,
    })
