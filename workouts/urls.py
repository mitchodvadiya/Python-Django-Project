"""
URL patterns for workout management.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.workout_list, name='workout_list'),
    path('add/', views.workout_create, name='workout_create'),
    path('<int:workout_id>/edit/', views.workout_edit, name='workout_edit'),
    path('<int:workout_id>/delete/', views.workout_delete, name='workout_delete'),
    path('my-plan/', views.my_workouts, name='my_workouts'),
]
