"""
Member model for storing detailed gym member records and trainer assignments.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='member_record')
    phone = models.CharField(max_length=15)
    address = models.TextField(blank=True)
    joining_date = models.DateField(default=timezone.now)
    assigned_trainer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_gym_members'
    )

    def __str__(self):
        full_name = self.user.get_full_name() or self.user.username
        return f"{full_name} ({self.phone})"

    @property
    def email(self):
        return self.user.email

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def account_status(self):
        if hasattr(self.user, 'profile'):
            return self.user.profile.get_status_display()
        return "Unknown"
