"""
Views for Membership Management (Module 5).
Handles plan creation, assignment, renewal, and active/expired filters.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from .models import MembershipPlan, MemberMembership
from .forms import MembershipPlanForm, AssignMembershipForm, RenewMembershipForm
from accounts.decorators import admin_required, member_required
from payments.models import Payment

@admin_required
def plan_list(request):
    """Admin view listing all created membership plans."""
    plans = MembershipPlan.objects.all().order_by('duration_days')
    return render(request, 'memberships/plan_list.html', {'plans': plans})

@admin_required
def plan_create(request):
    """Admin creates a new membership plan."""
    if request.method == 'POST':
        form = MembershipPlanForm(request.POST)
        if form.is_valid():
            plan = form.save()
            messages.success(request, f"Plan '{plan.name}' created successfully!")
            return redirect('plan_list')
    else:
        form = MembershipPlanForm()
    return render(request, 'memberships/plan_form.html', {'form': form, 'title': 'Create Membership Plan'})

@admin_required
def plan_edit(request, plan_id):
    """Admin edits an existing membership plan."""
    plan = get_object_or_404(MembershipPlan, id=plan_id)
    if request.method == 'POST':
        form = MembershipPlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            messages.success(request, f"Plan '{plan.name}' updated successfully!")
            return redirect('plan_list')
    else:
        form = MembershipPlanForm(instance=plan)
    return render(request, 'memberships/plan_form.html', {'form': form, 'title': f"Edit Plan: {plan.name}"})

@admin_required
def plan_delete(request, plan_id):
    """Admin deletes a membership plan with confirmation."""
    plan = get_object_or_404(MembershipPlan, id=plan_id)
    if request.method == 'POST':
        name = plan.name
        plan.delete()
        messages.success(request, f"Plan '{name}' was deleted.")
        return redirect('plan_list')
    return render(request, 'memberships/plan_confirm_delete.html', {'plan': plan})

@admin_required
def member_membership_list(request):
    """
    Admin view of all member subscriptions.
    Supports filtering by status: 'all', 'active', 'expired'.
    """
    today = timezone.now().date()
    # Auto-expire any memberships past their expiry date
    MemberMembership.objects.filter(status='active', expiry_date__lt=today).update(status='expired')
    
    status_filter = request.GET.get('status', 'all')
    queryset = MemberMembership.objects.select_related('member', 'plan').order_by('-start_date')
    
    if status_filter == 'active':
        queryset = queryset.filter(status='active')
    elif status_filter == 'expired':
        queryset = queryset.filter(status='expired')
        
    return render(request, 'memberships/member_membership_list.html', {
        'memberships': queryset,
        'status_filter': status_filter
    })

@admin_required
def assign_plan(request):
    """Admin assigns a membership plan to an approved member."""
    if request.method == 'POST':
        form = AssignMembershipForm(request.POST)
        if form.is_valid():
            member = form.cleaned_data['member']
            plan = form.cleaned_data['plan']
            start_date = form.cleaned_data['start_date']
            expiry_date = start_date + timedelta(days=plan.duration_days)
            
            # Expire previous active memberships for this member
            MemberMembership.objects.filter(member=member, status='active').update(status='expired')
            
            membership = MemberMembership.objects.create(
                member=member,
                plan=plan,
                start_date=start_date,
                expiry_date=expiry_date,
                status='active'
            )
            # Auto-create payment receipt for this plan assignment
            payment = Payment.objects.create(
                member=member,
                membership=membership,
                amount=plan.price,
                payment_date=start_date,
                payment_method='Cash',
                payment_status='Paid',
                notes=f"Membership fee receipt for plan: {plan.name}."
            )
            messages.success(request, f"Assigned '{plan.name}' to {member.get_full_name() or member.username}. Receipt #{payment.id} generated.")
            return redirect('member_membership_list')
    else:
        initial_member = request.GET.get('member_id')
        form = AssignMembershipForm(initial={'member': initial_member} if initial_member else None)
        
    return render(request, 'memberships/assign_plan.html', {'form': form})

@admin_required
def renew_membership(request, membership_id):
    """Admin renews an expired or active membership for a member."""
    old_membership = get_object_or_404(MemberMembership.objects.select_related('member', 'plan'), id=membership_id)
    
    if request.method == 'POST':
        form = RenewMembershipForm(request.POST)
        if form.is_valid():
            plan = form.cleaned_data['plan']
            start_date = form.cleaned_data['start_date']
            expiry_date = start_date + timedelta(days=plan.duration_days)
            
            # Mark old membership as expired
            old_membership.status = 'expired'
            old_membership.save()
            
            new_membership = MemberMembership.objects.create(
                member=old_membership.member,
                plan=plan,
                start_date=start_date,
                expiry_date=expiry_date,
                status='active'
            )
            # Auto-create renewal payment receipt
            payment = Payment.objects.create(
                member=old_membership.member,
                membership=new_membership,
                amount=plan.price,
                payment_date=start_date,
                payment_method='Cash',
                payment_status='Paid',
                notes=f"Renewal fee receipt for {plan.name}."
            )
            messages.success(request, f"Renewed membership for {old_membership.member.get_full_name() or old_membership.member.username} with {plan.name}! Receipt #{payment.id} generated.")
            return redirect('member_membership_list')
    else:
        # Default start date is day after old expiry if in future, else today
        today = timezone.now().date()
        default_start = old_membership.expiry_date + timedelta(days=1) if old_membership.expiry_date >= today else today
        form = RenewMembershipForm(initial={'plan': old_membership.plan, 'start_date': default_start})
        
    return render(request, 'memberships/renew_plan.html', {
        'form': form,
        'old_membership': old_membership
    })

@member_required
def enroll_plan(request, plan_id):
    """
    Member self-enrolls into a membership plan directly from their dashboard.
    Automatically generates active subscription and payment receipt.
    """
    plan = get_object_or_404(MembershipPlan, id=plan_id)
    today = timezone.now().date()
    expiry_date = today + timedelta(days=plan.duration_days)
    
    # Expire previous active memberships
    MemberMembership.objects.filter(member=request.user, status='active').update(status='expired')
    
    membership = MemberMembership.objects.create(
        member=request.user,
        plan=plan,
        start_date=today,
        expiry_date=expiry_date,
        status='active'
    )
    
    payment_method = request.POST.get('payment_method', 'UPI') if request.method == 'POST' else 'UPI'
    payment = Payment.objects.create(
        member=request.user,
        membership=membership,
        amount=plan.price,
        payment_date=today,
        payment_method=payment_method,
        payment_status='Paid',
        notes=f"Online enrollment receipt for package {plan.name}."
    )
    
    messages.success(request, f"Successfully enrolled in '{plan.name}'! Payment receipt #{payment.id} of Rs. {plan.price} has been generated.")
    return redirect('dashboard_member')

@admin_required
def membership_delete(request, membership_id):
    """Admin deletes an erroneous or duplicate membership record."""
    membership = get_object_or_404(MemberMembership, id=membership_id)
    if request.method == 'POST':
        member_name = membership.member.get_full_name() or membership.member.username
        plan_name = membership.plan.name
        membership.delete()
        messages.success(request, f"Subscription '{plan_name}' for {member_name} was removed.")
        return redirect('member_membership_list')
    return render(request, 'memberships/membership_confirm_delete.html', {'membership': membership})

