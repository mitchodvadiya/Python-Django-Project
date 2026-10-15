from django.contrib import admin
from .models import WorkoutPlan

@admin.register(WorkoutPlan)
class WorkoutPlanAdmin(admin.ModelAdmin):
    list_display = ('member', 'workout_day', 'exercise_name', 'sets', 'repetitions', 'assigned_trainer')
    list_filter = ('workout_day', 'assigned_trainer')
    search_fields = ('member__username', 'member__first_name', 'member__last_name', 'exercise_name')
