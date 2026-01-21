from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import ListView, DetailView, CreateView
from django.utils import timezone
from datetime import timedelta
from .mixins import *
from django.contrib import messages
from django.views import View


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

class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'main/task_detail.html'
    context_object_name = 'task'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)


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
    """ Показ детальной страницы для привычки пользователя """
    model = Habit
    template_name = 'main/habit_detail.html'
    context_object_name = 'habit'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Текущая привычка, которую показывает DetailView.
        # И сохраняем в переменную, чтобы удобнее работать
        habit = self.object

        period_days = 30
        start_date = timezone.now().date() - timedelta(days=period_days)

        # Логи привычки за период
        logs = HabitLog.objects.filter(
            habit=habit, # Берем логи только для текущей привычки.
            date__gte=start_date
        ).order_by('date')

        # Прогресс
        total_days = logs.count() # Сколько всего дней есть логов за период.
        done_days = logs.filter(is_done=True).count()
        progress_percent = int(done_days / total_days * 100) if total_days else 0

        # Проверяем, отмечена ли привычка сегодня
        today = timezone.now().date()
        done_today = HabitLog.objects.filter(habit=habit, date=today, is_done=True).exists()

        # Передаем в шаблон
        context.update({
            'logs': logs,
            'total_days': total_days,
            'done_days': done_days,
            'progress_percent': progress_percent,
            'period_days': period_days,
            'done_today': done_today,
            'title': f'История привычки: {habit.title}'
        })

        return context

# View:
# Здесь View — это класс из Django, точнее базовый класс для всех классовых представлений (Class-Based Views):
# Он не делает ничего сам по себе, но задаёт базовую структуру для классов, которые будут отвечать на HTTP-запросы (GET, POST, PUT, DELETE и т.д.).
# Любой класс-наследник View может переопределять методы вроде get() или post(), чтобы обработать соответствующие HTTP-запросы.

class HabitMarkDoneView(LoginRequiredMixin, View):
    """ Обрабатывает кнопку "Выполнено", которая отмечает привычку как выполненную сегодня """
    def post(self, request, slug):
        habit = get_object_or_404(Habit, slug=slug, user=request.user)
        today = timezone.now().date()

        # Проверяем, есть ли лог за сегодня
        # Проверяет, есть ли уже запись для этой привычки на сегодня.
        # Если нет — создает новую с is_done=True
        log, created = HabitLog.objects.get_or_create(
            habit=habit,
            date=today,
            defaults={'is_done': True}
        )
        if not created:
            messages.info(request, "Вы уже отметили эту привычку сегодня!")
        else:
            messages.success(request, f"Привычка '{habit.title}' отмечена как выполненная сегодня!")

        return redirect('habit_detail', slug=habit.slug)



class UserLoginView(LoginView):
    """ Вход пользователя в систему """
    form_class = CustomLoginForm
    template_name = 'main/login.html'
    redirect_authenticated_user = True
    extra_context = {'title': 'Вход'}

    def form_valid(self, form):
        messages.success(
            self.request,
            f"Добро пожаловать, {form.get_user().username}!"
        )
        return super().form_valid(form)


class UserLogoutView(LogoutView):
    """ Выход пользователя из системы """
    # next_page можно убрать, используем LOGOUT_REDIRECT_URL из settings.py
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "Вы успешно вышли из системы")
        return super().dispatch(request, *args, **kwargs)

class UserSignUpView(CreateView):
    """ Регистрация пользователя на сайте """
    form_class = CustomSingUpForm
    template_name = 'main/signup.html'
    success_url = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        # Чтобы залогиненный пользователь не мог зайти на /signup/.
        if request.user.is_authenticated:
            # Если user уже авторизированн его редиректит на страницу home
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(
            self.request,
            "Регистрация прошла успешно. Теперь вы можете войти."
        )
        return super().form_valid(form)




