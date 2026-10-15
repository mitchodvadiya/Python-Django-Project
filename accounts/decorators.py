"""
Custom permission decorators for role-based access control.
Ensures only approved users with correct roles access protected views.
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    """View decorator ensuring current user is an approved Administrator."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Superusers always have admin access
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
            
        profile = getattr(request.user, 'profile', None)
        if not profile:
            messages.error(request, "Account profile missing. Access denied.")
            return redirect('access_denied')
            
        if profile.status == 'pending':
            return redirect('pending_approval')
        elif profile.status != 'approved':
            messages.error(request, f"Your account status is: {profile.get_status_display()}. Access denied.")
            return redirect('access_denied')
            
        if profile.role != 'admin':
            messages.error(request, "Administrator privileges required. Access denied.")
            return redirect('access_denied')
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def trainer_required(view_func):
    """View decorator - Trainer portal and dashboard are disabled."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        messages.error(request, "Trainer portal is disabled. Access denied.")
        return redirect('access_denied')
    return _wrapped_view

def member_required(view_func):
    """View decorator ensuring current user is an approved Member."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
            
        profile = getattr(request.user, 'profile', None)
        if not profile:
            messages.error(request, "Account profile missing. Access denied.")
            return redirect('access_denied')
            
        if profile.status == 'pending':
            return redirect('pending_approval')
        elif profile.status != 'approved':
            messages.error(request, f"Your account status is: {profile.get_status_display()}. Access denied.")
            return redirect('access_denied')
            
        if profile.role != 'member':
            messages.error(request, "Member privileges required. Access denied.")
            return redirect('access_denied')
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view
