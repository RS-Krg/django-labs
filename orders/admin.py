from django.contrib import admin

from .models import Order, OrderItem
from .services import cancel_order


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('variant', 'product_name', 'size', 'price', 'quantity')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user', 'full_name', 'status', 'created_at', 'total_price')
    list_filter = ('status', 'created_at')
    search_fields = ('full_name', 'phone', 'user__username')
    readonly_fields = ('user', 'status', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    actions = ['mark_confirmed', 'mark_shipped', 'mark_done', 'cancel']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user').prefetch_related('items')

    @admin.display(description='Сумма, ₽')
    def total_price(self, order):
        return order.total_price

    def _move(self, request, queryset, from_status, to_status):
        updated = queryset.filter(status=from_status).update(status=to_status)
        self.message_user(request, f'Изменено заказов: {updated}')

    @admin.action(description='Подтвердить')
    def mark_confirmed(self, request, queryset):
        self._move(request, queryset, Order.Status.NEW, Order.Status.CONFIRMED)

    @admin.action(description='Передать в доставку')
    def mark_shipped(self, request, queryset):
        self._move(request, queryset, Order.Status.CONFIRMED, Order.Status.SHIPPED)

    @admin.action(description='Отметить выполненными')
    def mark_done(self, request, queryset):
        self._move(request, queryset, Order.Status.SHIPPED, Order.Status.DONE)

    @admin.action(description='Отменить и вернуть товары на склад')
    def cancel(self, request, queryset):
        count = 0
        for order in queryset.filter(status__in=[Order.Status.NEW, Order.Status.CONFIRMED]):
            count += cancel_order(order)
        self.message_user(request, f'Отменено заказов: {count}')
