from django.contrib import admin
from .models import MembershipPlan, MemberMembership

@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration_days', 'price')

@admin.register(MemberMembership)
class MemberMembershipAdmin(admin.ModelAdmin):
    list_display = ('member', 'plan', 'start_date', 'expiry_date', 'status')
    list_filter = ('status', 'plan', 'start_date')
    search_fields = ('member__username', 'member__first_name', 'member__last_name')
