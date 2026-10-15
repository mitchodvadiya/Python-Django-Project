"""
Forms for membership plan management, assignment, and renewals.
"""

from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from .models import MembershipPlan, MemberMembership

class MembershipPlanForm(forms.ModelForm):
    class Meta:
        model = MembershipPlan
        fields = ['name', 'duration_days', 'price', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class AssignMembershipForm(forms.Form):
    member = forms.ModelChoiceField(
        queryset=User.objects.filter(profile__role='member', profile__status='approved'),
        required=True,
        empty_label="-- Select Approved Member --"
    )
    plan = forms.ModelChoiceField(
        queryset=MembershipPlan.objects.all(),
        required=True,
        empty_label="-- Select Plan --"
    )
    start_date = forms.DateField(
        initial=timezone.now,
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )

class RenewMembershipForm(forms.Form):
    plan = forms.ModelChoiceField(
        queryset=MembershipPlan.objects.all(),
        required=True,
        empty_label="-- Select Plan --"
    )
    start_date = forms.DateField(
        initial=timezone.now,
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )
