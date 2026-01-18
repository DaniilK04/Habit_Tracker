from django.utils import timezone
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import *

class TaskFilterForm(forms.Form):
    search = forms.CharField(
        required=False,
        label='',
        widget=forms.TextInput(attrs={
            'placeholder': 'Поиск по названию задачи'
        })
    )

    sort = forms.ChoiceField(
        choices=[
            ('-created_at', 'Сначала новые'),
            ('created_at', 'Сначала старые'),
            ('priority', 'Приоритет ↑'),
            ('-priority', 'Приоритет ↓'),
            ('deadline', 'Ближайший дедлайн'),
            ('-deadline', 'Самый поздний дедлайн'),
        ],
        required=False,
        label='Сортировка'
    )

    status = forms.ChoiceField(
        choices=(('', 'Все'),) + Task.STATUS_CHOICES,
        required=False,
        label='Статус'
    )

class HabitFilterForm(forms.Form):
    search = forms.CharField(
        required=False,
        label='',
        widget=forms.TextInput(attrs={
            'placeholder': 'Поиск по названию привычки'
        })
    )

    active = forms.ChoiceField(
        choices=[
            ('', 'Все'),
            ('true', 'Активна'),
            ('false', 'Не активна'),
        ],
        required=False,
        label='Активность'
    )

    frequency = forms.ChoiceField(
        choices=(('', 'Все'),) + Habit.FREQUENCY_CHOICES,
        required=False,
        label='Частота выполнения'
    )

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description',
                  'status', 'priority',
                  'deadline',
                  ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Название задачи'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Описание задачи'
            }),
            'deadline': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-input'
            }),
        }

    def clean_deadline(self):
        deadline = self.cleaned_data['deadline']
        if deadline < timezone.now().date():
            raise forms.ValidationError(
                'Дедлайн не может быть в прошлом'
            )
        return deadline

class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = ['title', 'frequency', 'start_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Название привычки'
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-input'
            }),
        }

    def clean_start_date(self):
        start_date = self.cleaned_data['start_date']
        if start_date > timezone.now().date():
            raise forms.ValidationError(
                'Дата начала не может быть в будущем'
            )
        return start_date