"""
URL configuration for gym_system project.
Maps URL routes to views across accounts, members, trainers, memberships, payments, attendance, workouts, and reports.
"""

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def home_redirect(request):
    """Redirect home route based on login status."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')

urlpatterns = [
    # App URL Includes
    path('', include('accounts.urls')),
    
    # Django Admin site
    path('admin/', admin.site.urls),
    
    # Root redirect
    path('', home_redirect, name='home'),
    path('members/', include('members.urls')),
    path('memberships/', include('memberships.urls')),
    path('payments/', include('payments.urls')),
    path('attendance/', include('attendance.urls')),
    path('workouts/', include('workouts.urls')),
    path('reports/', include('reports.urls')),
]
