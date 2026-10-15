"""
Views for Attendance Management (Module 7).
Handles check-in, check-out, duplicate prevention, correction, and history.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import Attendance
from .forms import CheckInForm, CheckOutForm, AttendanceEditForm
from accounts.decorators import admin_required, member_required

@admin_required
def attendance_list(request):
    """
    Admin view of attendance records.
    Filters by selected date (defaults to today) or displays all records.
    """
    date_filter = request.GET.get('date', timezone.now().date().strftime('%Y-%m-%d'))
    view_all = request.GET.get('all', 'false') == 'true'
    
    if view_all:
        records = Attendance.objects.select_related('member').all()
        date_filter = None
    else:
        records = Attendance.objects.select_related('member').filter(attendance_date=date_filter)
        
    currently_inside = Attendance.objects.filter(attendance_date=timezone.now().date(), check_out_time__isnull=True).count()
    
    return render(request, 'attendance/attendance_list.html', {
        'records': records,
        'date_filter': date_filter,
        'view_all': view_all,
        'currently_inside': currently_inside,
    })

@admin_required
def mark_attendance(request):
    """
    Records a new member check-in.
    Enforces rule against duplicate active check-ins.
    """
    if request.method == 'POST':
        form = CheckInForm(request.POST)
        if form.is_valid():
            member = form.cleaned_data['member']
            attendance_date = form.cleaned_data['attendance_date']
            check_in_time = form.cleaned_data['check_in_time']
            
            Attendance.objects.create(
                member=member,
                attendance_date=attendance_date,
                check_in_time=check_in_time
            )
            messages.success(request, f"Check-in recorded for {member.get_full_name() or member.username} at {check_in_time}.")
            return redirect('attendance_list')
    else:
        now_time = timezone.localtime().strftime('%H:%M')
        form = CheckInForm(initial={'check_in_time': now_time})
        
    return render(request, 'attendance/mark_attendance.html', {'form': form})

@admin_required
def record_checkout(request, attendance_id):
    """Records check-out time for an active check-in record."""
    attendance = get_object_or_404(Attendance, id=attendance_id)
    if request.method == 'POST':
        now_time = timezone.localtime().time()
        attendance.check_out_time = now_time
        attendance.save()
        messages.success(request, f"Check-out recorded for {attendance.member.get_full_name() or attendance.member.username} at {now_time.strftime('%H:%M')}.")
    return redirect('attendance_list')

@admin_required
def attendance_edit(request, attendance_id):
    """Admin corrects or modifies attendance record."""
    attendance = get_object_or_404(Attendance, id=attendance_id)
    if request.method == 'POST':
        form = AttendanceEditForm(request.POST, instance=attendance)
        if form.is_valid():
            form.save()
            messages.success(request, f"Attendance record #{attendance.id} corrected successfully.")
            return redirect('attendance_list')
    else:
        form = AttendanceEditForm(instance=attendance)
        
    return render(request, 'attendance/attendance_edit.html', {
        'form': form,
        'attendance': attendance
    })

@admin_required
def attendance_delete(request, attendance_id):
    """Admin deletes an erroneous attendance entry."""
    attendance = get_object_or_404(Attendance, id=attendance_id)
    if request.method == 'POST':
        attendance.delete()
        messages.success(request, f"Attendance record #{attendance_id} was removed.")
        return redirect('attendance_list')
    return render(request, 'attendance/attendance_confirm_delete.html', {'attendance': attendance})

@member_required
def my_attendance(request):
    """Member views their own personal attendance log."""
    records = Attendance.objects.filter(member=request.user).order_by('-attendance_date', '-check_in_time')
    return render(request, 'attendance/my_attendance.html', {'records': records})
