from django.contrib import admin
from .models import *

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'status',
        'priority',
        'deadline',
        'created_at',
        'user'
    )
    list_display_links = (
        'id',
        'title'
    )
    list_editable = (
        'status',
        'priority',
    )
    search_fields = (
        'title',
    )
    list_filter = (
        'status',
        'priority'
    )
    prepopulated_fields = {'slug': ('title',)}
    ordering = (
        'id',
    )
    readonly_fields = ('id',)
    list_select_related = ('user',)


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'frequency',
        'start_date',
        'is_active',
        'user',
    )
    list_display_links = (
        'id',
        'title'
    )
    list_editable = (
        'is_active',
        'frequency'
    )
    search_fields = (
        'title',
    )
    list_filter = (
        'frequency',
        'is_active'
    )
    prepopulated_fields = {'slug': ('title',)}
    ordering = (
        'id',
    )
    readonly_fields = ('id',)
    list_select_related = ('user',)


@admin.register(HabitLog)
class HabitLogAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'habit',
        'date',
        'is_done'
    )
    list_select_related = ('habit',)
    list_display_links = (
        'id',
        'habit'
    )
    list_editable = (
        'is_done',
    )
    search_fields = (
        'habit__title',
    )
    list_filter = (
        'is_done',
    )
    ordering = (
        'id',
    )
    readonly_fields = ('id',)