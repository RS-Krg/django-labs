from django.contrib.auth.models import Group, Permission, User
from django.core.management.base import BaseCommand

from helpdesk.models import Category, Ticket


class Command(BaseCommand):
    help = 'Создаёт категории, демонстрационных сотрудников и заявки без дублей'

    def handle(self, *args, **options):
        for name in ('Оборудование', 'Программы', 'Доступы и учётные записи', 'Сеть и интернет'):
            Category.objects.get_or_create(name=name)
        group, _ = Group.objects.get_or_create(name='ИТ-отдел')
        group.permissions.add(*Permission.objects.filter(
            content_type__app_label='helpdesk', codename__in=['view_ticket', 'change_ticket'],
        ))
        employee, created = User.objects.get_or_create(username='ivanov', defaults={
            'first_name': 'Иван', 'last_name': 'Иванов',
        })
        if created:
            employee.set_password('Zayavka-2026')
            employee.save()
        specialist, created = User.objects.get_or_create(username='petrov', defaults={
            'first_name': 'Пётр', 'last_name': 'Петров',
        })
        if created:
            specialist.set_password('Zayavka-2026')
            specialist.save()
        specialist.groups.add(group)
        Ticket.objects.get_or_create(
            title='Не печатает принтер', created_by=employee,
            defaults={'author': 'Иван Иванов', 'category': Category.objects.get(name='Оборудование')},
        )
        self.stdout.write(self.style.SUCCESS('Демонстрационные данные готовы.'))
