from datetime import timedelta

from django import forms
from django.utils import timezone


class ReportPeriodForm(forms.Form):
    date_from = forms.DateField(label='С', widget=forms.DateInput(attrs={'type': 'date'}))
    date_to = forms.DateField(label='По', widget=forms.DateInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        if not args and 'data' not in kwargs:
            today = timezone.localdate()
            kwargs.setdefault('initial', {'date_from': today - timedelta(days=29), 'date_to': today})
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('date_from')
        end = cleaned.get('date_to')
        if start and end and start > end:
            raise forms.ValidationError('Дата начала должна быть не позже даты окончания.')
        return cleaned
