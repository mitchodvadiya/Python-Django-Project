"""
Attendance model for tracking member daily gym visits, check-in, and check-out times.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Attendance(models.Model):
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendances')
    attendance_date = models.DateField(default=timezone.now)
    check_in_time = models.TimeField(default=timezone.now)
    check_out_time = models.TimeField(null=True, blank=True)

    class Meta:
        ordering = ['-attendance_date', '-check_in_time']

    def __str__(self):
        member_name = self.member.get_full_name() or self.member.username
        status = f"Checked out at {self.check_out_time}" if self.check_out_time else "Currently Active (In Gym)"
        return f"{member_name} - {self.attendance_date} ({status})"

    @property
    def is_currently_inside(self):
        return self.check_out_time is None
