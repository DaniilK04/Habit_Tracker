from django.urls import path
from .views import *


urlpatterns = [
    path('', HomeListView.as_view(), name='home'),
    path('tasks/', TasksListView.as_view(), name='task'),
    path('tasks/add/', TaskAddView.as_view(), name='task_add'),
    path('habits/', HabitsListView.as_view(), name='habit'),
    path('habits/add/', HabitsAddView.as_view(), name='habit_add'),
    path('habits/<slug:slug>/', HabitsDetailView.as_view(), name='habit_detail')

]