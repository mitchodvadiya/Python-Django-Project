"""
URL patterns for attendance management.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.attendance_list, name='attendance_list'),
    path('check-in/', views.mark_attendance, name='mark_attendance'),
    path('<int:attendance_id>/check-out/', views.record_checkout, name='record_checkout'),
    path('<int:attendance_id>/edit/', views.attendance_edit, name='attendance_edit'),
    path('<int:attendance_id>/delete/', views.attendance_delete, name='attendance_delete'),
    path('my-history/', views.my_attendance, name='my_attendance'),
]
