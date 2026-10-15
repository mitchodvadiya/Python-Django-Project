from django.contrib import admin
from .models import Attendance

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('member', 'attendance_date', 'check_in_time', 'check_out_time')
    list_filter = ('attendance_date',)
    search_fields = ('member__username', 'member__first_name', 'member__last_name')
