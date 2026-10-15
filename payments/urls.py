"""
URL patterns for payment management.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.payment_list, name='payment_list'),
    path('record/', views.payment_create, name='payment_create'),
    path('<int:payment_id>/edit/', views.payment_edit, name='payment_edit'),
    path('<int:payment_id>/delete/', views.payment_delete, name='payment_delete'),
    path('my-history/', views.my_payments, name='my_payments'),
    path('<int:payment_id>/receipt/', views.payment_receipt, name='payment_receipt'),
]
