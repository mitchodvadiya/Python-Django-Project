"""
URL patterns for authentication, dashboards, and user approval workflow.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Authentication routes
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('pending-approval/', views.pending_approval_view, name='pending_approval'),
    path('access-denied/', views.access_denied_view, name='access_denied'),
    
    # Dashboard router and role-specific dashboards
    path('dashboard/', views.dashboard_router, name='dashboard'),
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard/member/', views.dashboard_member, name='dashboard_member'),
    
    # User approval management (Admin only)
    path('approvals/', views.pending_users_list, name='pending_users_list'),
    path('approvals/<int:user_id>/approve/', views.approve_user, name='approve_user'),
    path('approvals/<int:user_id>/reject/', views.reject_user, name='reject_user'),
    path('approvals/<int:user_id>/toggle-status/', views.toggle_user_active, name='toggle_user_active'),
]
