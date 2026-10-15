"""
Models for membership plans and member subscriptions.
Includes automatic expiry calculation using Python datetime and timedelta.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class MembershipPlan(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="e.g. Monthly, Quarterly, Half-Yearly, Yearly")
    duration_days = models.PositiveIntegerField(help_text="Duration in days (e.g. 30, 90, 180, 365)")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price in INR / USD")
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} - {self.duration_days} Days (Rs. {self.price})"

class MemberMembership(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('expired', 'Expired'),
    )

    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    plan = models.ForeignKey(MembershipPlan, on_delete=models.CASCADE, related_name='subscriptions')
    start_date = models.DateField(default=timezone.now)
    expiry_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.member.get_full_name() or self.member.username} - {self.plan.name} ({self.status.capitalize()})"

    def save(self, *args, **kwargs):
        # Automatically calculate expiry date based on plan duration if not explicitly provided
        if not self.expiry_date and self.plan and self.start_date:
            self.expiry_date = self.start_date + timedelta(days=self.plan.duration_days)
        
        # Check and update status based on current date
        if self.expiry_date and self.expiry_date < timezone.now().date():
            self.status = 'expired'
            
        super().save(*args, **kwargs)

    @property
    def is_currently_active(self):
        return self.status == 'active' and self.expiry_date >= timezone.now().date()

    @property
    def days_remaining(self):
        if self.expiry_date:
            delta = (self.expiry_date - timezone.now().date()).days
            return max(0, delta)
        return 0
