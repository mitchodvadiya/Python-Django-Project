"""
Views for user authentication, registration, approval workflow, and dashboards.
Implements function-based views demonstrating standard Django MVT patterns.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone

from .models import UserProfile
from .forms import UserRegistrationForm, UserLoginForm
from .decorators import admin_required, member_required

def register_view(request):
    """
    Handles member and trainer public registration.
    Sets status to 'pending' for administrator review.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone = form.cleaned_data['phone']
            address = form.cleaned_data.get('address', '')
            
            # Create standard User with hashed password
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Create associated UserProfile with 'pending' status
            UserProfile.objects.create(
                user=user,
                role='member',
                status='pending',
                phone=phone,
                address=address,
                joining_date=timezone.now().date()
            )
            
            # Create Member record
            from members.models import Member
            Member.objects.create(
                user=user,
                phone=phone,
                address=address,
                joining_date=timezone.now().date()
            )
                
            messages.success(request, f"Registration submitted for '{username}'! Your account is pending administrator approval.")
            return redirect('pending_approval')
    else:
        form = UserRegistrationForm()
        
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    """
    Handles user authentication and redirects to appropriate dashboard based on role and status.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Handle superuser administrator
                if user.is_superuser:
                    # Ensure profile exists for superuser
                    profile, created = UserProfile.objects.get_or_create(
                        user=user,
                        defaults={'role': 'admin', 'status': 'approved'}
                    )
                    login(request, user)
                    messages.success(request, f"Welcome Administrator {user.username}!")
                    return redirect('dashboard_admin')
                
                # Check user profile status
                profile = getattr(user, 'profile', None)
                if not profile:
                    messages.error(request, "Account profile not found. Please contact administrator.")
                    return redirect('login')
                    
                if profile.status == 'pending':
                    messages.warning(request, "Your registration is pending administrator approval.")
                    return redirect('pending_approval')
                elif profile.status == 'rejected':
                    messages.error(request, "Your registration request was rejected by the administrator.")
                    return redirect('access_denied')
                elif profile.status == 'deactivated' or not user.is_active:
                    messages.error(request, "Your account has been deactivated. Please contact gym administrator.")
                    return redirect('access_denied')
                if profile.role == 'trainer':
                    messages.error(request, "Trainer portal is disabled. Trainers do not have direct login access.")
                    return redirect('login')
                elif profile.status == 'approved':
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
                    return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = UserLoginForm()
        
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    """Logs out current user and redirects to login."""
    logout(request)
    messages.info(request, "You have been successfully logged out.")
    return redirect('login')

def pending_approval_view(request):
    """Informational page shown to pending registrants."""
    return render(request, 'accounts/pending_approval.html')

def access_denied_view(request):
    """Shown when user tries to access unauthorized resources."""
    return render(request, 'accounts/access_denied.html')

def dashboard_router(request):
    """
    Routes authenticated approved user to their specific dashboard.
    """
    if not request.user.is_authenticated:
        return redirect('login')
        
    if request.user.is_superuser:
        return redirect('dashboard_admin')
        
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return redirect('access_denied')
        
    if profile.status == 'pending':
        return redirect('pending_approval')
    elif profile.status != 'approved':
        return redirect('access_denied')
        
    if profile.role == 'admin':
        return redirect('dashboard_admin')
    elif profile.role == 'member':
        return redirect('dashboard_member')
    elif profile.role == 'trainer':
        messages.error(request, "Trainer dashboard is disabled.")
        return redirect('access_denied')
        
    return redirect('access_denied')

@admin_required
def dashboard_admin(request):
    """
    Module 2: Admin Dashboard
    Displays gym statistics: members, trainers, pending requests, memberships, and payments.
    """
    # Import relevant models lazily to avoid circular imports
    from memberships.models import MemberMembership
    from payments.models import Payment
    
    total_approved_members = UserProfile.objects.filter(role='member', status='approved').count()
    pending_registrations = UserProfile.objects.filter(status='pending').count()
    
    # Update memberships status before querying
    today = timezone.now().date()
    MemberMembership.objects.filter(status='active', expiry_date__lt=today).update(status='expired')
    
    active_memberships = MemberMembership.objects.filter(status='active').count()
    expired_memberships = MemberMembership.objects.filter(status='expired').count()
    
    total_payments = Payment.objects.filter(payment_status='Paid').aggregate(total=Sum('amount'))['total'] or 0
    pending_payments_count = Payment.objects.filter(payment_status='Pending').count()
    
    # Recent pending requests for quick review
    pending_users = UserProfile.objects.filter(status='pending').select_related('user').order_by('-user__date_joined')[:5]

    context = {
        'total_approved_members': total_approved_members,
        'pending_registrations': pending_registrations,
        'active_memberships': active_memberships,
        'expired_memberships': expired_memberships,
        'total_payments': total_payments,
        'pending_payments_count': pending_payments_count,
        'pending_users': pending_users,
    }
    return render(request, 'accounts/dashboard_admin.html', context)

@member_required
def dashboard_member(request):
    """
    Member Dashboard:
    Displays member profile, membership plan & expiry, trainer, workout plan, recent attendance & payments.
    """
    from members.models import Member
    from memberships.models import MemberMembership, MembershipPlan
    from payments.models import Payment
    from attendance.models import Attendance
    from workouts.models import WorkoutPlan
    
    # Ensure membership expiration is checked
    today = timezone.now().date()
    MemberMembership.objects.filter(member=request.user, status='active', expiry_date__lt=today).update(status='expired')
    
    member_details = Member.objects.filter(user=request.user).first()
    active_membership = MemberMembership.objects.filter(member=request.user, status='active').order_by('-expiry_date').first()
    past_memberships = MemberMembership.objects.filter(member=request.user).exclude(id=active_membership.id if active_membership else None).order_by('-expiry_date')
    available_plans = MembershipPlan.objects.all().order_by('duration_days')
    
    workout_plans = WorkoutPlan.objects.filter(member=request.user).order_by('workout_day')
    recent_attendance = Attendance.objects.filter(member=request.user).order_by('-attendance_date', '-check_in_time')[:7]
    # Auto-generate payment receipt if active membership does not have one yet
    if active_membership and not Payment.objects.filter(membership=active_membership).exists():
        Payment.objects.create(
            member=request.user,
            membership=active_membership,
            amount=active_membership.plan.price,
            payment_date=active_membership.start_date,
            payment_method='Cash',
            payment_status='Paid',
            notes=f"Membership fee receipt for {active_membership.plan.name}."
        )

    active_payment = Payment.objects.filter(member=request.user, membership=active_membership).order_by('-id').first() if active_membership else None
    recent_payments = Payment.objects.filter(member=request.user).select_related('membership', 'membership__plan').order_by('-payment_date', '-id')[:5]

    days_remaining = None
    if active_membership and active_membership.expiry_date:
        days_remaining = (active_membership.expiry_date - today).days

    context = {
        'member_user': request.user,
        'profile': request.user.profile,
        'member_details': member_details,
        'active_membership': active_membership,
        'active_payment': active_payment,
        'past_memberships': past_memberships,
        'available_plans': available_plans,
        'days_remaining': days_remaining,
        'workout_plans': workout_plans,
        'recent_attendance': recent_attendance,
        'recent_payments': recent_payments,
    }
    return render(request, 'accounts/dashboard_member.html', context)

# ==================== User Approval Management (Admin Only) ====================

@admin_required
def pending_users_list(request):
    """Displays all pending registration requests."""
    pending_profiles = UserProfile.objects.filter(status='pending').select_related('user').order_by('-user__date_joined')
    return render(request, 'accounts/pending_users.html', {'pending_profiles': pending_profiles})

@admin_required
def approve_user(request, user_id):
    """Approves a pending registration request."""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        profile = get_object_or_404(UserProfile, user=user)
        profile.status = 'approved'
        profile.save()
        user.is_active = True
        user.save()
        messages.success(request, f"Account '{user.username}' has been approved as {profile.get_role_display()}.")
    return redirect('pending_users_list')

@admin_required
def reject_user(request, user_id):
    """Rejects a registration request."""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        profile = get_object_or_404(UserProfile, user=user)
        profile.status = 'rejected'
        profile.save()
        user.is_active = False
        user.save()
        messages.warning(request, f"Registration request for '{user.username}' has been rejected.")
    return redirect('pending_users_list')

@admin_required
def toggle_user_active(request, user_id):
    """Toggles account activation status between approved and deactivated."""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        profile = get_object_or_404(UserProfile, user=user)
        if profile.status == 'approved':
            profile.status = 'deactivated'
            user.is_active = False
            messages.warning(request, f"Account '{user.username}' has been deactivated.")
        elif profile.status == 'deactivated':
            profile.status = 'approved'
            user.is_active = True
            messages.success(request, f"Account '{user.username}' has been reactivated.")
        profile.save()
        user.save()
    return redirect(request.META.get('HTTP_REFERER', 'dashboard_admin'))
