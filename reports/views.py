"""
Views for Module 9: Reports.
Renders plain HTML tables for members, trainers, pending requests, memberships, payments, attendance, and workouts.
"""

from django.shortcuts import render
from django.db.models import Sum, Count
from django.utils import timezone

from accounts.models import UserProfile
from accounts.decorators import admin_required
from members.models import Member
from memberships.models import MemberMembership
from payments.models import Payment
from attendance.models import Attendance
from workouts.models import WorkoutPlan

@admin_required
def report_overview(request):
    """Index page linking to all specific reports."""
    stats = {
        'total_members': UserProfile.objects.filter(role='member', status='approved').count(),
        'total_pending': UserProfile.objects.filter(status='pending').count(),
        'active_memberships': MemberMembership.objects.filter(status='active').count(),
        'total_revenue': Payment.objects.filter(payment_status='Paid').aggregate(s=Sum('amount'))['s'] or 0,
        'total_attendance': Attendance.objects.count(),
        'total_workouts': WorkoutPlan.objects.count(),
    }
    return render(request, 'reports/report_overview.html', {'stats': stats})

@admin_required
def report_members(request):
    """Detailed members report table."""
    members = Member.objects.select_related('user', 'assigned_trainer', 'user__profile').all().order_by('-joining_date')
    return render(request, 'reports/members_report.html', {'members': members})

@admin_required
def report_pending(request):
    """Pending user approvals report table."""
    pending_users = UserProfile.objects.filter(status='pending').select_related('user').order_by('-user__date_joined')
    return render(request, 'reports/pending_report.html', {'pending_users': pending_users})

@admin_required
def report_memberships(request):
    """Active and expired memberships report table."""
    today = timezone.now().date()
    MemberMembership.objects.filter(status='active', expiry_date__lt=today).update(status='expired')
    memberships = MemberMembership.objects.select_related('member', 'plan').all().order_by('-start_date')
    return render(request, 'reports/memberships_report.html', {'memberships': memberships})

@admin_required
def report_payments(request):
    """Payments collections report with paid and pending sums."""
    payments = Payment.objects.select_related('member', 'membership', 'membership__plan').all().order_by('-payment_date')
    total_paid = payments.filter(payment_status='Paid').aggregate(s=Sum('amount'))['s'] or 0
    total_pending = payments.filter(payment_status='Pending').aggregate(s=Sum('amount'))['s'] or 0
    return render(request, 'reports/payments_report.html', {
        'payments': payments,
        'total_paid': total_paid,
        'total_pending': total_pending,
    })

@admin_required
def report_attendance(request):
    """Attendance history report table."""
    attendances = Attendance.objects.select_related('member').all().order_by('-attendance_date', '-check_in_time')
    return render(request, 'reports/attendance_report.html', {'attendances': attendances})

@admin_required
def report_workouts(request):
    """Workout assignments report table."""
    workouts = WorkoutPlan.objects.select_related('member', 'assigned_trainer').all().order_by('workout_day', 'member__username')
    return render(request, 'reports/workouts_report.html', {'workouts': workouts})
