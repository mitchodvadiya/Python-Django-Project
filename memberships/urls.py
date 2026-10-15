"""
URL patterns for membership management.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('plans/', views.plan_list, name='plan_list'),
    path('plans/add/', views.plan_create, name='plan_create'),
    path('plans/<int:plan_id>/edit/', views.plan_edit, name='plan_edit'),
    path('plans/<int:plan_id>/delete/', views.plan_delete, name='plan_delete'),
    path('plans/<int:plan_id>/enroll/', views.enroll_plan, name='enroll_plan'),
    
    path('subscriptions/', views.member_membership_list, name='member_membership_list'),
    path('assign/', views.assign_plan, name='assign_plan'),
    path('<int:membership_id>/renew/', views.renew_membership, name='renew_membership'),
    path('<int:membership_id>/delete/', views.membership_delete, name='membership_delete'),
]
