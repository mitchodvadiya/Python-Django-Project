"""
Payment model for tracking membership and fee collections.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from memberships.models import MemberMembership

class Payment(models.Model):
    METHOD_CHOICES = (
        ('Cash', 'Cash'),
        ('Card', 'Credit/Debit Card'),
        ('UPI', 'UPI (Google Pay, PhonePe, Paytm)'),
        ('Net Banking', 'Net Banking'),
    )

    STATUS_CHOICES = (
        ('Paid', 'Paid'),
        ('Pending', 'Pending'),
    )

    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    membership = models.ForeignKey(
        MemberMembership,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='Cash')
    payment_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Paid')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment #{self.id} - {self.member.get_full_name() or self.member.username} (Rs. {self.amount} - {self.payment_status})"
