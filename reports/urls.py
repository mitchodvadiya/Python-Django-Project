"""
URL patterns for reports.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.report_overview, name='report_overview'),
    path('members/', views.report_members, name='report_members'),
    path('pending/', views.report_pending, name='report_pending'),
    path('memberships/', views.report_memberships, name='report_memberships'),
    path('payments/', views.report_payments, name='report_payments'),
    path('attendance/', views.report_attendance, name='report_attendance'),
    path('workouts/', views.report_workouts, name='report_workouts'),
]
