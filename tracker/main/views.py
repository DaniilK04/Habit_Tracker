from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from .forms import *
from .models import *
from django.views.generic import ListView, DetailView, CreateView
from django.utils import timezone
from datetime import timedelta
from .mixins import *


class HomeListView(LoginRequiredMixin, ListView, TaskFilterMixin):
    """ Главная страница. Отображает:
                        активные задачи
                        ближайшие дедлайны
                        активные привычки
                        процент выполнения привычек за неделю """
    model = Task
    template_name = 'main/home.html'
    context_object_name = 'tasks'
    paginate_by = 7
    form_class = TaskFilterForm

    def get_queryset(self):
        queryset = Task.objects.filter(user=self.request.user)
        return self.get_filtered_queryset(queryset)

    def get_habit_progress(self, user):
        week_ago = timezone.now().date() - timedelta(days=7)

        total = HabitLog.objects.filter(
            habit__user=user,
            date__gte=week_ago
        ).count()

        done = HabitLog.objects.filter(
            habit__user=user,
            date__gte=week_ago,
            is_done=True
        ).count()

        if total == 0:
            return 0

        return int(done / total * 100)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['title'] = 'Главная страница'
        # форма
        context['form'] = self.form_class(self.request.GET)
        # активные привычки
        context['habits'] = Habit.objects.filter(
            user=user,
            is_active=True
        )
        # ближайшие дедлайны (например 5)
        context['near_deadlines'] = Task.objects.filter(
            user=user,
            status__in=['Todo', 'In_progress']
        ).order_by('deadline')[:5]
        # процент выполнения привычек за неделю
        context['habit_progress'] = self.get_habit_progress(user)

        return context


class TasksListView(LoginRequiredMixin, ListView, TaskFilterMixin):
    """ Список задач. Функционал:
                    фильтр по статусу
                    сортировка по дедлайну / приоритету
                    поиск по названию
                    пагинация """
    model = Task
    template_name = 'main/tasks.html'
    context_object_name = 'tasks'
    paginate_by = 7
    form_class = TaskFilterForm

    def get_queryset(self):
        queryset = Task.objects.filter(user=self.request.user)
        return self.get_filtered_queryset(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['form'] = self.form_class(self.request.GET)
        context['title'] = 'Задачи'

        return context


class TaskAddView(LoginRequiredMixin, CreateView):
    """ Создание задачи """
    model = Task
    form_class = TaskForm
    template_name = 'main/add_task.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.user = self.request.user
        # Django: берёт success_url и делает redirect('home')
        return super().form_valid(form)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавление задачи'
        return context

class HabitsListView(LoginRequiredMixin, ListView):
    """ Список привычек с поиском и фильтрацией """
    model = Habit
    template_name = 'main/habits.html'
    context_object_name = 'habits'
    paginate_by = 7
    form_class = HabitFilterForm

    def get_queryset(self):
        queryset = Habit.objects.filter(user=self.request.user)

        form = self.form_class(self.request.GET)
        if form.is_valid():
            cd = form.cleaned_data

            if cd.get('search'):
                queryset = queryset.filter(title__icontains=cd['search'])

            if cd.get('active') == 'true':
                queryset = queryset.filter(is_active=True)
            elif cd.get('active') == 'false':
                queryset = queryset.filter(is_active=False)

            if cd.get('frequency'):
                queryset = queryset.filter(frequency=cd['frequency'])

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(self.request.GET)
        context['title'] = 'Привычки'
        return context


class HabitsAddView(LoginRequiredMixin, CreateView):
    """ Создание привычки """
    model = Habit
    form_class = HabitForm
    template_name = 'main/add_habit.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.user = self.request.user
        # Django: берёт success_url и делает redirect('home')
        return super().form_valid(form)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавление привычки'
        return context


class HabitsDetailView(LoginRequiredMixin, DetailView):
    model = Habit
    template_name = 'main/habit_detail.html'
    context_object_name = 'habit'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        """
        Ограничиваем доступ:
        пользователь может видеть ТОЛЬКО свои привычки
        """
        return Habit.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        habit = self.object  # текущая привычка

        # период (например последние 30 дней)
        period_days = 30
        start_date = timezone.now().date() - timedelta(days=period_days)

        # логи привычки за период
        logs = HabitLog.objects.filter(
            habit=habit,
            date__gte=start_date
        ).order_by('date')

        # статистика
        total_days = logs.count()
        done_days = logs.filter(is_done=True).count()

        if total_days > 0:
            progress_percent = int(done_days / total_days * 100)
        else:
            progress_percent = 0

        # передаём всё в шаблон
        context['logs'] = logs
        context['total_days'] = total_days
        context['done_days'] = done_days
        context['progress_percent'] = progress_percent
        context['period_days'] = period_days
        context['title'] = f'История привычки: {habit.title}'

        return context





