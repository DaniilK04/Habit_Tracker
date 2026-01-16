from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.conf import settings

class Task(models.Model):
    title = models.CharField(
        verbose_name='Название',
        max_length=200
    )
    description = models.TextField (
        verbose_name='Описание',
        blank=True,
        default='Нет описания'
    )
    STATUS_CHOICES = (
        ('todo', 'Не начал'),
        ('in_progress', 'В процессе'),
        ('done', 'Сделано')
    )
    status = models.CharField(
        verbose_name='Статус',
        choices=STATUS_CHOICES,
        max_length=30,
        default='Todo',
    )
    PRIORITY_CHOICES = (
        (1, 'Низкий'),
        (2, 'Средний'),
        (3, 'Высокий'),
    )
    priority = models.IntegerField(
        choices=PRIORITY_CHOICES,
        default=1,
        verbose_name='Приоритет'
    )
    deadline = models.DateField(
        verbose_name='Дата конца'
    )
    created_at = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True
    )
    slug = models.SlugField(
        max_length=255,
        blank=True,
        verbose_name='URL'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name='user_task',
        db_index=True
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title, allow_unicode=True)
            slug = base_slug
            counter = 1
            while Task.objects.filter(user=self.user, slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title}, {self.user}"

    def get_absolute_url(self):
        return reverse('task', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ["-created_at"]
        db_table_comment = "Задачи пользователя"


class Habit(models.Model):
    title = models.CharField(
        verbose_name='Название',
        max_length=200
    )
    FREQUENCY_CHOICES = (
        ('Daily', 'Каждый день'),
        ('Weekly', 'Каждую неделю'),
        ('Day_about', 'Через день')
    )
    frequency = models.CharField(
        verbose_name='Частота выполнения',
        choices=FREQUENCY_CHOICES,
        max_length=20,
        default='Daily',
    )
    start_date = models.DateField(
        verbose_name='Начало привычки',
    )
    is_active = models.BooleanField(
        verbose_name='Активна',
        default=True,
        db_index=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name='user_habit',
        db_index=True
    )
    slug = models.SlugField(
        max_length=255,
        blank=True,
        verbose_name='URL'
    )
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title, allow_unicode=True)
            slug = base_slug
            counter = 1
            while Habit.objects.filter(user=self.user, slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title}, {self.user}"

    def get_absolute_url(self):
        return reverse('habit', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ["title"]
        db_table_comment = "Привычки пользователя"


class HabitLog(models.Model):
    habit = models.ForeignKey(
        Habit,
        on_delete=models.PROTECT,
        verbose_name='Привычка',
        related_name='habit_log',
        db_index=True
    )
    date = models.DateField(
        verbose_name='Дата выполнения',
    )
    is_done = models.BooleanField(
        verbose_name='Выполнено',
        default=True,
        db_index=True
    )

    def __str__(self):
        return f"{self.habit} — {self.date}"

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ["habit"]
