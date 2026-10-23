from django.contrib.auth.models import Group, Permission
from django.core.management import call_command
from django.core.management.base import BaseCommand

from accounts.models import User


class Command(BaseCommand):
    help = 'Создаёт каталог и демонстрационных покупателя и менеджера'

    def handle(self, *args, **options):
        call_command('seed_catalog')
        group, _ = Group.objects.get_or_create(name='Менеджеры')
        group.permissions.add(*Permission.objects.filter(
            content_type__app_label='orders', codename__in=['view_order', 'change_order', 'view_orderitem'],
        ), *Permission.objects.filter(
            content_type__app_label='catalog', codename__in=[
                'view_product', 'change_product', 'view_productvariant',
                'add_productvariant', 'change_productvariant',
            ],
        ))
        buyer, created = User.objects.get_or_create(username='buyer', defaults={
            'first_name': 'Анна', 'last_name': 'Смирнова', 'email': 'buyer@example.test',
        })
        if created:
            buyer.set_password('ShopDemo-2026')
            buyer.save()
        manager, created = User.objects.get_or_create(username='manager', defaults={
            'first_name': 'Менеджер', 'email': 'manager@example.test', 'is_staff': True,
        })
        if created:
            manager.set_password('ShopDemo-2026')
            manager.save()
        manager.groups.add(group)
        self.stdout.write(self.style.SUCCESS('Демонстрационные пользователи готовы.'))
