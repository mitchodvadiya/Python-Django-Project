from django.contrib import admin
from .models import Member

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'assigned_trainer', 'joining_date')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone')
    list_filter = ('joining_date', 'assigned_trainer')
