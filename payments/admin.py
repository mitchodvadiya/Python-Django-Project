from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'member', 'amount', 'payment_date', 'payment_method', 'payment_status')
    list_filter = ('payment_status', 'payment_method', 'payment_date')
    search_fields = ('member__username', 'member__first_name', 'member__last_name')
