"""
Models for accounts application.
Extends Django built-in User with role and approval status.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Administrator & Trainer'),
        ('member', 'Member'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('deactivated', 'Deactivated'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    specialization = models.CharField(max_length=100, blank=True)
    joining_date = models.DateField(default=timezone.now)

    def __str__(self):
        full_name = self.user.get_full_name() or self.user.username
        return f"{full_name} ({self.get_role_display()} - {self.get_status_display()})"

    @property
    def is_admin(self):
        return self.role == 'admin' or self.user.is_superuser

    @property
    def is_trainer(self):
        return self.role == 'admin' or self.user.is_superuser

    @property
    def is_member(self):
        return self.role == 'member'

    @property
    def is_approved(self):
        return self.status == 'approved' and self.user.is_active
