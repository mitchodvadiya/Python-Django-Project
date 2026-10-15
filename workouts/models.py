"""
WorkoutPlan model for assigning structured exercise routines to members by day of the week.
"""

from django.db import models
from django.contrib.auth.models import User

class WorkoutPlan(models.Model):
    DAY_CHOICES = (
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    )

    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_plans')
    assigned_trainer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='trainer_workouts'
    )
    exercise_name = models.CharField(max_length=100)
    sets = models.PositiveIntegerField(default=3)
    repetitions = models.CharField(max_length=50, default="12 reps")
    workout_day = models.CharField(max_length=20, choices=DAY_CHOICES, default='Monday')
    instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['workout_day', 'exercise_name']

    def __str__(self):
        return f"{self.member.get_full_name() or self.member.username} - {self.workout_day}: {self.exercise_name} ({self.sets} sets x {self.repetitions})"
