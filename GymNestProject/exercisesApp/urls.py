from django.urls import path
from . import views
app_name = 'exercisesAppName'
urlpatterns = [
    path('exercises/', views.exercises_list, name='exercises_list'),
    path('exercises/progress/', views.progress_tracking, name='progress_tracking'),
    path('exercises/progress/add/', views.add_progress, name='add_progress'),
    path('exercises/progress/delete/<int:progress_id>/', views.delete_progress, name='delete_progress'),
]
