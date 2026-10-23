from django import forms
from django.contrib.auth import get_user_model

from .models import Ticket


class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'


class TicketForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'author', 'category', 'priority', 'description']
        widgets = {'description': forms.Textarea(attrs={'rows': 5})}
        help_texts = {'author': 'ФИО или подразделение, от которого пришла заявка'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = '— не выбрана —'

    def clean_title(self):
        title = self.cleaned_data['title'].strip()
        if len(title) < 5:
            raise forms.ValidationError('Сформулируйте тему хотя бы в 5 символов.')
        return title


class TicketProcessForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['status', 'assignee']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assignee = self.fields['assignee']
        assignee.queryset = get_user_model().objects.filter(groups__name='ИТ-отдел')
        assignee.empty_label = '— не назначен —'
