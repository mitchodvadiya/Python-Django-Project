"""
Views for Payment Management (Module 6).
Handles recording payments, viewing histories, status filters, and totals.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from .models import Payment
from .forms import PaymentForm
from accounts.decorators import admin_required, member_required

@admin_required
def payment_list(request):
    """
    Admin view of all payments.
    Calculates total collections and allows filtering by Paid vs Pending.
    """
    status_filter = request.GET.get('status', 'all')
    queryset = Payment.objects.select_related('member', 'membership', 'membership__plan').order_by('-payment_date', '-id')
    
    if status_filter in ['Paid', 'Pending']:
        queryset = queryset.filter(payment_status=status_filter)
        
    total_paid = Payment.objects.filter(payment_status='Paid').aggregate(total=Sum('amount'))['total'] or 0
    total_pending = Payment.objects.filter(payment_status='Pending').aggregate(total=Sum('amount'))['total'] or 0
    
    return render(request, 'payments/payment_list.html', {
        'payments': queryset,
        'status_filter': status_filter,
        'total_paid': total_paid,
        'total_pending': total_pending,
    })

@admin_required
def payment_create(request):
    """Admin records a new payment."""
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save()
            messages.success(request, f"Payment of Rs. {payment.amount} recorded for {payment.member.get_full_name() or payment.member.username} ({payment.payment_status}).")
            return redirect('payment_list')
    else:
        member_id = request.GET.get('member_id')
        form = PaymentForm(initial={'member': member_id} if member_id else None)
        
    return render(request, 'payments/payment_form.html', {'form': form, 'title': 'Record New Payment'})

@admin_required
def payment_edit(request, payment_id):
    """Admin edits payment record details."""
    payment = get_object_or_404(Payment, id=payment_id)
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            payment = form.save()
            messages.success(request, f"Payment record #{payment.id} updated successfully.")
            return redirect('payment_list')
    else:
        form = PaymentForm(instance=payment)
        
    return render(request, 'payments/payment_form.html', {'form': form, 'title': f"Edit Payment #{payment.id}"})

@admin_required
def payment_delete(request, payment_id):
    """Admin deletes payment record."""
    payment = get_object_or_404(Payment, id=payment_id)
    if request.method == 'POST':
        payment.delete()
        messages.success(request, f"Payment record #{payment_id} was deleted.")
        return redirect('payment_list')
    return render(request, 'payments/payment_confirm_delete.html', {'payment': payment})

@member_required
def my_payments(request):
    """Member views their own personal payment history."""
    payments = Payment.objects.filter(member=request.user).select_related('membership', 'membership__plan').order_by('-payment_date')
    total_paid = payments.filter(payment_status='Paid').aggregate(total=Sum('amount'))['total'] or 0
    return render(request, 'payments/my_payments.html', {
        'payments': payments,
        'total_paid': total_paid
    })

def payment_receipt(request, payment_id):
    """
    Displays an official, printable fee receipt.
    Accessible to the member who made the payment or gym administrators.
    """
    if not request.user.is_authenticated:
        return redirect('login')
        
    payment = get_object_or_404(
        Payment.objects.select_related('member', 'member__profile', 'membership', 'membership__plan'),
        id=payment_id
    )
    
    is_admin = request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == 'admin')
    if not is_admin and payment.member != request.user:
        messages.error(request, "You are not authorized to view this payment receipt.")
        return redirect('access_denied')
        
    return render(request, 'payments/payment_receipt.html', {
        'payment': payment,
        'is_admin': is_admin,
    })
