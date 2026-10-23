from django.contrib import admin

from .models import Category, Ticket


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'priority', 'status', 'assignee', 'created_at')
    list_filter = ('status', 'priority', 'category')
    search_fields = ('title', 'author', 'description')
    list_select_related = ('category', 'assignee')
