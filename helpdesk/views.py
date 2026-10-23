from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import TicketForm, TicketProcessForm
from .models import Ticket


def visible_tickets(user):
    tickets = Ticket.objects.select_related('category', 'assignee', 'created_by')
    if user.has_perm('helpdesk.change_ticket'):
        return tickets
    return tickets.filter(created_by=user)


def hello(request):
    return HttpResponse('Привет! Это учёт заявок ИТ-отдела.')


@login_required
def ticket_list(request):
    tickets = visible_tickets(request.user).order_by('-created_at')
    status = request.GET.get('status', '')
    query = request.GET.get('q', '').strip()
    if status:
        tickets = tickets.filter(status=status)
    if query:
        tickets = tickets.filter(Q(title__icontains=query) | Q(author__icontains=query) |
                                 Q(description__icontains=query))
    return render(request, 'helpdesk/ticket_list.html', {
        'tickets': tickets, 'statuses': Ticket.Status.choices, 'status': status, 'query': query,
    })


@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(visible_tickets(request.user), pk=pk)
    context = {'ticket': ticket, 'can_edit': ticket.can_be_edited_by(request.user)}
    if request.user.has_perm('helpdesk.change_ticket'):
        context['process_form'] = TicketProcessForm(instance=ticket)
    return render(request, 'helpdesk/ticket_detail.html', context)


@login_required
def ticket_create(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.save()
            messages.success(request, f'Заявка №{ticket.pk} зарегистрирована.')
            return redirect(ticket)
    else:
        user = request.user
        form = TicketForm(initial={'author': user.get_full_name() or user.username})
    return render(request, 'helpdesk/ticket_form.html', {'form': form, 'page_title': 'Новая заявка'})


@login_required
def ticket_update(request, pk):
    ticket = get_object_or_404(visible_tickets(request.user), pk=pk)
    if not ticket.can_be_edited_by(request.user):
        raise PermissionDenied
    if request.method == 'POST':
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            messages.success(request, 'Изменения сохранены.')
            return redirect(ticket)
    else:
        form = TicketForm(instance=ticket)
    return render(request, 'helpdesk/ticket_form.html', {
        'form': form, 'page_title': f'Заявка №{ticket.pk}: редактирование',
    })


@require_POST
@permission_required('helpdesk.change_ticket', raise_exception=True)
def ticket_process(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    form = TicketProcessForm(request.POST, instance=ticket)
    if form.is_valid():
        form.save()
        messages.success(request, 'Заявка обновлена.')
    else:
        messages.error(request, 'Не удалось обновить заявку: проверьте значения полей.')
    return redirect(ticket)
