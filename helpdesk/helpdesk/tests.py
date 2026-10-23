from django.contrib.auth.models import Group, Permission, User
from django.test import TestCase
from django.urls import reverse

from .models import Ticket


class TicketAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.employee = User.objects.create_user('ivanov', password='test-pass-123')
        cls.colleague = User.objects.create_user('sidorov', password='test-pass-123')
        cls.it_user = User.objects.create_user('petrov', password='test-pass-123')
        it_group = Group.objects.create(name='ИТ-отдел')
        it_group.permissions.add(
            Permission.objects.get(content_type__app_label='helpdesk', codename='change_ticket'),
            Permission.objects.get(content_type__app_label='helpdesk', codename='view_ticket'),
        )
        cls.it_user.groups.add(it_group)
        cls.own_ticket = Ticket.objects.create(
            title='Не печатает принтер', author='Иванов', created_by=cls.employee,
        )
        cls.foreign_ticket = Ticket.objects.create(
            title='Нет доступа к 1С', author='Сидоров', created_by=cls.colleague,
        )

    def test_anonymous_is_redirected_to_login(self):
        url = reverse('ticket_list')
        self.assertRedirects(self.client.get(url), f"{reverse('login')}?next={url}")

    def test_employee_sees_only_own_tickets(self):
        self.client.force_login(self.employee)
        response = self.client.get(reverse('ticket_list'))
        self.assertContains(response, self.own_ticket.title)
        self.assertNotContains(response, self.foreign_ticket.title)

    def test_employee_cannot_open_foreign_ticket(self):
        self.client.force_login(self.employee)
        self.assertEqual(self.client.get(self.foreign_ticket.get_absolute_url()).status_code, 404)

    def test_created_ticket_belongs_to_current_user(self):
        self.client.force_login(self.employee)
        response = self.client.post(reverse('ticket_create'), {
            'title': 'Сломалась мышь', 'author': 'Иванов', 'priority': 'normal',
        })
        ticket = Ticket.objects.get(title='Сломалась мышь')
        self.assertEqual(ticket.created_by, self.employee)
        self.assertRedirects(response, ticket.get_absolute_url())

    def test_short_title_is_rejected(self):
        self.client.force_login(self.employee)
        response = self.client.post(reverse('ticket_create'), {
            'title': 'abc', 'author': 'Иванов', 'priority': 'normal',
        })
        self.assertContains(response, 'хотя бы в 5 символов')
        self.assertFalse(Ticket.objects.filter(title='abc').exists())

    def test_employee_cannot_process_ticket(self):
        self.client.force_login(self.employee)
        response = self.client.post(reverse('ticket_process', args=[self.own_ticket.pk]), {'status': 'done'})
        self.assertEqual(response.status_code, 403)

    def test_it_user_can_process_ticket(self):
        self.client.force_login(self.it_user)
        self.client.post(reverse('ticket_process', args=[self.foreign_ticket.pk]), {
            'status': 'in_progress', 'assignee': self.it_user.pk,
        })
        self.foreign_ticket.refresh_from_db()
        self.assertEqual(self.foreign_ticket.status, Ticket.Status.IN_PROGRESS)
        self.assertEqual(self.foreign_ticket.assignee, self.it_user)

    def test_employee_cannot_edit_started_ticket(self):
        self.own_ticket.status = Ticket.Status.IN_PROGRESS
        self.own_ticket.save()
        self.client.force_login(self.employee)
        self.assertEqual(self.client.get(reverse('ticket_update', args=[self.own_ticket.pk])).status_code, 403)

    def test_assignee_must_be_it_member(self):
        self.client.force_login(self.it_user)
        self.client.post(reverse('ticket_process', args=[self.own_ticket.pk]), {
            'status': 'in_progress', 'assignee': self.employee.pk,
        })
        self.own_ticket.refresh_from_db()
        self.assertEqual(self.own_ticket.status, Ticket.Status.NEW)

    def test_search_and_status_filter_keep_scope(self):
        self.client.force_login(self.employee)
        response = self.client.get(reverse('ticket_list'), {'q': 'принтер', 'status': 'new'})
        self.assertContains(response, self.own_ticket.title)
        self.assertNotContains(response, self.foreign_ticket.title)
