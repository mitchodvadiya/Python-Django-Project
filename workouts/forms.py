"""
Forms for creating and modifying workout plans.
Restricts member choices based on user role (Admin vs Trainer).
"""

from django import forms
from django.contrib.auth.models import User
from .models import WorkoutPlan
from members.models import Member

class WorkoutPlanForm(forms.ModelForm):
    class Meta:
        model = WorkoutPlan
        fields = ['member', 'workout_day', 'exercise_name', 'sets', 'repetitions', 'instructions']
        widgets = {
            'instructions': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Admin selects any approved gym member
        self.fields['member'].queryset = User.objects.filter(profile__role='member', profile__status='approved')
        self.fields['member'].empty_label = "-- Select Approved Member --"
