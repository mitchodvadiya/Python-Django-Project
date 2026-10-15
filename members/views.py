"""
Views for Member Management (Module 3).
Handles CRUD, search, trainer assignment, and member profile view/update.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from .models import Member
from .forms import MemberCreateForm, MemberEditForm, MemberSelfEditForm, AssignTrainerMembershipForm
from accounts.models import UserProfile
from accounts.decorators import admin_required, member_required
from memberships.models import MemberMembership, MembershipPlan

@admin_required
def member_list(request):
    """
    Displays all members with search functionality across name, username, and phone.
    """
    search_query = request.GET.get('q', '').strip()
    members = Member.objects.select_related('user', 'assigned_trainer', 'user__profile').all().order_by('-joining_date')
    
    if search_query:
        members = members.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
        
    return render(request, 'members/member_list.html', {
        'members': members,
        'search_query': search_query
    })

@admin_required
def member_create(request):
    """
    Admin creates an approved member directly.
    """
    if request.method == 'POST':
        form = MemberCreateForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            phone = form.cleaned_data['phone']
            address = form.cleaned_data['address']
            membership_plan = form.cleaned_data['membership_plan']
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            # Create approved UserProfile
            UserProfile.objects.create(
                user=user,
                role='member',
                status='approved',
                phone=phone,
                address=address,
                joining_date=timezone.now().date()
            )
            # Create Member record with Admin as Trainer
            member = Member.objects.create(
                user=user,
                phone=phone,
                address=address,
                joining_date=timezone.now().date(),
                assigned_trainer=request.user
            )
            
            # Assign initial membership if selected
            if membership_plan:
                from payments.models import Payment
                start_date = timezone.now().date()
                expiry_date = start_date + timedelta(days=membership_plan.duration_days)
                membership = MemberMembership.objects.create(
                    member=user,
                    plan=membership_plan,
                    start_date=start_date,
                    expiry_date=expiry_date,
                    status='active'
                )
                Payment.objects.create(
                    member=user,
                    membership=membership,
                    amount=membership_plan.price,
                    payment_date=start_date,
                    payment_method='Cash',
                    payment_status='Paid',
                    notes=f"Initial membership fee receipt for {membership_plan.name}."
                )
                
            messages.success(request, f"Member '{user.get_full_name() or user.username}' added successfully!")
            return redirect('member_list')
    else:
        form = MemberCreateForm()
        
    return render(request, 'members/member_form.html', {'form': form, 'title': 'Add New Member'})

@admin_required
def member_detail(request, member_id):
    """
    Admin view of full member details: membership, payments, attendance, and workouts.
    """
    member = get_object_or_404(Member.objects.select_related('user', 'assigned_trainer', 'user__profile'), id=member_id)
    
    # Auto-expire memberships if date passed
    today = timezone.now().date()
    MemberMembership.objects.filter(member=member.user, status='active', expiry_date__lt=today).update(status='expired')
    
    memberships = member.user.memberships.select_related('plan').order_by('-start_date')
    payments = member.user.payments.all().order_by('-payment_date')
    attendances = member.user.attendances.all().order_by('-attendance_date', '-check_in_time')[:10]
    workouts = member.user.workout_plans.all().order_by('workout_day')
    
    return render(request, 'members/member_detail.html', {
        'member': member,
        'memberships': memberships,
        'payments': payments,
        'attendances': attendances,
        'workouts': workouts,
    })

@admin_required
def member_edit(request, member_id):
    """
    Admin edits member contact information and trainer assignment.
    """
    member = get_object_or_404(Member, id=member_id)
    if request.method == 'POST':
        form = MemberEditForm(request.POST, instance=member)
        if form.is_valid():
            member = form.save()
            # Update user model fields
            member.user.first_name = form.cleaned_data['first_name']
            member.user.last_name = form.cleaned_data['last_name']
            member.user.email = form.cleaned_data['email']
            member.user.save()
            
            # Sync user profile phone & address
            if hasattr(member.user, 'profile'):
                member.user.profile.phone = member.phone
                member.user.profile.address = member.address
                member.user.profile.save()
                
            messages.success(request, f"Member '{member.full_name}' updated successfully!")
            return redirect('member_detail', member_id=member.id)
    else:
        form = MemberEditForm(instance=member)
        
    return render(request, 'members/member_form.html', {'form': form, 'title': f"Edit Member: {member.full_name}"})

@admin_required
def member_delete(request, member_id):
    """
    Admin deletes member account with confirmation.
    """
    member = get_object_or_404(Member, id=member_id)
    user = member.user
    if request.method == 'POST':
        user_name = member.full_name
        user.delete() # Cascades to profile, member record, memberships, attendance, workouts
        messages.success(request, f"Member '{user_name}' was deleted successfully.")
        return redirect('member_list')
        
    return render(request, 'members/member_confirm_delete.html', {'member': member})

@admin_required
def member_assign(request, member_id):
    """
    Admin assigns trainer and/or new membership plan to a member.
    """
    member = get_object_or_404(Member, id=member_id)
    active_membership = MemberMembership.objects.filter(member=member.user, status='active').first()
    
    if request.method == 'POST':
        form = AssignTrainerMembershipForm(request.POST)
        if form.is_valid():
            new_plan = form.cleaned_data['membership_plan']
            member.assigned_trainer = request.user
            member.save()
            
            if new_plan:
                if not active_membership or active_membership.plan != new_plan:
                    start_date = timezone.now().date()
                    expiry_date = start_date + timedelta(days=new_plan.duration_days)
                    MemberMembership.objects.filter(member=member.user, status='active').update(status='expired')
                    membership = MemberMembership.objects.create(
                        member=member.user,
                        plan=new_plan,
                        start_date=start_date,
                        expiry_date=expiry_date,
                        status='active'
                    )
                    from payments.models import Payment
                    payment = Payment.objects.create(
                        member=member.user,
                        membership=membership,
                        amount=new_plan.price,
                        payment_date=start_date,
                        payment_method='Cash',
                        payment_status='Paid',
                        notes=f"Membership fee receipt for plan: {new_plan.name}."
                    )
                    messages.success(request, f"Updated plan to '{new_plan.name}' for {member.full_name}. Receipt #{payment.id} generated.")
                else:
                    messages.success(request, f"Active plan '{active_membership.plan.name}' preserved for {member.full_name}.")
            else:
                messages.success(request, f"Updated member details for {member.full_name}.")
                
            return redirect('member_detail', member_id=member.id)
    else:
        form = AssignTrainerMembershipForm(initial={
            'membership_plan': active_membership.plan if active_membership else None
        })
        
    return render(request, 'members/assign_trainer_membership.html', {
        'member': member,
        'form': form,
        'active_membership': active_membership
    })

@member_required
def member_profile_edit(request):
    """
    Allows logged-in member to update their own permitted contact details.
    """
    member = get_object_or_404(Member, user=request.user)
    if request.method == 'POST':
        form = MemberSelfEditForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.save()
            
            if hasattr(request.user, 'profile'):
                request.user.profile.phone = member.phone
                request.user.profile.address = member.address
                request.user.profile.save()
                
            messages.success(request, "Your profile details have been updated.")
            return redirect('dashboard_member')
    else:
        form = MemberSelfEditForm(instance=member)
        
    return render(request, 'members/profile_edit.html', {'form': form})
