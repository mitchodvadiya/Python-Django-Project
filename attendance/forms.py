"""
Forms for recording check-in, check-out, and correcting attendance.
"""

from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Attendance

class CheckInForm(forms.Form):
    member = forms.ModelChoiceField(
        queryset=User.objects.filter(profile__role='member', profile__status='approved'),
        required=True,
        empty_label="-- Select Member for Check-in --"
    )
    attendance_date = forms.DateField(
        initial=timezone.now,
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )
    check_in_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        required=True
    )

    def clean(self):
        cleaned_data = super().clean()
        member = cleaned_data.get('member')
        date = cleaned_data.get('attendance_date')
        
        if member and date:
            # Check for active check-in without check-out on this date
            active_checkin = Attendance.objects.filter(
                member=member,
                attendance_date=date,
                check_out_time__isnull=True
            ).exists()
            if active_checkin:
                raise forms.ValidationError(
                    f"Member {member.get_full_name() or member.username} is already checked in on {date} without a check-out time. Please record check-out first."
                )
        return cleaned_data

class CheckOutForm(forms.Form):
    check_out_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        required=True
    )

class AttendanceEditForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['member', 'attendance_date', 'check_in_time', 'check_out_time']
        widgets = {
            'attendance_date': forms.DateInput(attrs={'type': 'date'}),
            'check_in_time': forms.TimeInput(attrs={'type': 'time'}),
            'check_out_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['member'].queryset = User.objects.filter(profile__role='member', profile__status='approved')
