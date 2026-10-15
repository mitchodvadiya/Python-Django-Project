"""
Forms for creating and editing payments.
"""

from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Payment
from memberships.models import MemberMembership

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['member', 'membership', 'amount', 'payment_date', 'payment_method', 'payment_status', 'notes']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['member'].queryset = User.objects.filter(profile__role='member', profile__status='approved')
        self.fields['member'].empty_label = "-- Select Member --"
        self.fields['membership'].empty_label = "-- Select Membership (Optional) --"
