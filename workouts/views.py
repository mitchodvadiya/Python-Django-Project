"""
Views for Workout Management (Module 8).
Handles workout creation by trainers/admin, and read-only viewing by members.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import WorkoutPlan
from .forms import WorkoutPlanForm
from accounts.decorators import member_required
from members.models import Member

def workout_list(request):
    """
    Displays workout plans list.
    Admin (Coach) manages and sees all workout plans.
    """
    if not request.user.is_authenticated:
        return redirect('login')
        
    profile = getattr(request.user, 'profile', None)
    if not request.user.is_superuser and (not profile or profile.status != 'approved'):
        return redirect('access_denied')
        
    day_filter = request.GET.get('day')
    member_filter = request.GET.get('member_id')
    
    if request.user.is_superuser or (profile and profile.role == 'admin'):
        queryset = WorkoutPlan.objects.select_related('member', 'assigned_trainer').all()
    elif profile and profile.role == 'member':
        return redirect('my_workouts')
    else:
        return redirect('access_denied')
        
    if day_filter:
        queryset = queryset.filter(workout_day=day_filter)
    if member_filter:
        queryset = queryset.filter(member_id=member_filter)
        
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    return render(request, 'workouts/workout_list.html', {
        'workouts': queryset,
        'days': days,
        'selected_day': day_filter,
    })

def workout_create(request):
    """
    Admin (Trainer) creates a new workout routine entry for a member.
    """
    if not request.user.is_authenticated:
        return redirect('login')
        
    profile = getattr(request.user, 'profile', None)
    is_admin = request.user.is_superuser or (profile and profile.role == 'admin' and profile.status == 'approved')
    
    if not is_admin:
        messages.error(request, "Only Administrators can assign workout plans.")
        return redirect('access_denied')
        
    if request.method == 'POST':
        form = WorkoutPlanForm(request.POST, user=request.user)
        if form.is_valid():
            workout = form.save(commit=False)
            workout.assigned_trainer = request.user
            workout.save()
            messages.success(request, f"Added {workout.exercise_name} ({workout.workout_day}) for {workout.member.get_full_name() or workout.member.username}.")
            return redirect('workout_list')
    else:
        member_id = request.GET.get('member_id')
        form = WorkoutPlanForm(user=request.user, initial={'member': member_id} if member_id else None)
        
    return render(request, 'workouts/workout_form.html', {'form': form, 'title': 'Add Workout Plan Entry'})

def workout_edit(request, workout_id):
    """
    Admin edits a workout routine entry.
    """
    workout = get_object_or_404(WorkoutPlan, id=workout_id)
    profile = getattr(request.user, 'profile', None)
    is_admin = request.user.is_superuser or (profile and profile.role == 'admin')
    
    if not is_admin:
        messages.error(request, "You are not authorized to edit this workout plan.")
        return redirect('access_denied')
        
    if request.method == 'POST':
        form = WorkoutPlanForm(request.POST, instance=workout, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Workout entry '{workout.exercise_name}' updated successfully.")
            return redirect('workout_list')
    else:
        form = WorkoutPlanForm(instance=workout, user=request.user)
        
    return render(request, 'workouts/workout_form.html', {'form': form, 'title': f"Edit Workout: {workout.exercise_name}"})

def workout_delete(request, workout_id):
    """
    Admin deletes a workout entry.
    """
    workout = get_object_or_404(WorkoutPlan, id=workout_id)
    profile = getattr(request.user, 'profile', None)
    is_admin = request.user.is_superuser or (profile and profile.role == 'admin')
    
    if not is_admin:
        messages.error(request, "You are not authorized to delete this workout plan.")
        return redirect('access_denied')
        
    if request.method == 'POST':
        name = workout.exercise_name
        workout.delete()
        messages.success(request, f"Workout entry '{name}' removed successfully.")
        return redirect('workout_list')
        
    return render(request, 'workouts/workout_confirm_delete.html', {'workout': workout})

@member_required
def my_workouts(request):
    """
    Member views their own assigned workout routine (read-only).
    Organized by day of the week.
    """
    workouts = WorkoutPlan.objects.filter(member=request.user).select_related('assigned_trainer').order_by('workout_day')
    
    # Group workouts by day
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    workouts_by_day = {day: [] for day in days}
    for item in workouts:
        if item.workout_day in workouts_by_day:
            workouts_by_day[item.workout_day].append(item)
            
    return render(request, 'workouts/my_workouts.html', {
        'workouts_by_day': workouts_by_day,
        'has_workouts': workouts.exists(),
    })
