"""
URL patterns for member management.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.member_list, name='member_list'),
    path('add/', views.member_create, name='member_create'),
    path('<int:member_id>/', views.member_detail, name='member_detail'),
    path('<int:member_id>/edit/', views.member_edit, name='member_edit'),
    path('<int:member_id>/delete/', views.member_delete, name='member_delete'),
    path('<int:member_id>/assign/', views.member_assign, name='member_assign'),
    path('profile/edit/', views.member_profile_edit, name='member_profile_edit'),
]
