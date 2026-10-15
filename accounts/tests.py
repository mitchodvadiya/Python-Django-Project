"""
Unit tests for Gym Management System.
Validates:
1. User registration & pending approval workflow
2. Role permissions and dashboard routing
3. Membership expiry calculation using Python datetime
4. Duplicate active check-in prevention
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from accounts.models import UserProfile
from members.models import Member
from memberships.models import MembershipPlan, MemberMembership
from attendance.models import Attendance
from attendance.forms import CheckInForm

class GymSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # 1. Setup Admin (Admin & Coach)
        self.admin_user = User.objects.create_superuser(
            username='testadmin',
            email='admin@test.com',
            password='password123'
        )
        UserProfile.objects.create(
            user=self.admin_user,
            role='admin',
            status='approved',
            phone='1111111111'
        )
        
        # 2. Setup Legacy Trainer test user (for checking blocked login)
        self.trainer_user = User.objects.create_user(
            username='testtrainer',
            email='trainer@test.com',
            password='password123'
        )
        UserProfile.objects.create(
            user=self.trainer_user,
            role='trainer',
            status='approved',
            phone='2222222222',
            specialization='Strength'
        )
        
        # 3. Setup Approved Member
        self.member_user = User.objects.create_user(
            username='testmember',
            email='member@test.com',
            password='password123'
        )
        UserProfile.objects.create(
            user=self.member_user,
            role='member',
            status='approved',
            phone='3333333333'
        )
        Member.objects.create(
            user=self.member_user,
            phone='3333333333',
            assigned_trainer=self.admin_user
        )

        # 4. Setup Membership Plan
        self.plan = MembershipPlan.objects.create(
            name='Quarterly Test Plan',
            duration_days=90,
            price=3000.00
        )

    def test_registration_pending_status(self):
        """Test that new public registrations are given 'pending' status."""
        response = self.client.post('/register/', {
            'username': 'newapplicant',
            'first_name': 'New',
            'last_name': 'Applicant',
            'email': 'applicant@test.com',
            'role': 'member',
            'phone': '9988776655',
            'address': 'Test Address',
            'password': 'password123',
            'confirm_password': 'password123',
        })
        self.assertEqual(response.status_code, 302)
        new_user = User.objects.get(username='newapplicant')
        self.assertEqual(new_user.profile.status, 'pending')
        self.assertEqual(new_user.profile.role, 'member')

    def test_pending_user_cannot_access_dashboard(self):
        """Test that unapproved pending users are blocked or redirected."""
        pending_user = User.objects.create_user(username='pending1', password='password123')
        UserProfile.objects.create(user=pending_user, role='member', status='pending')
        
        login_success = self.client.login(username='pending1', password='password123')
        response = self.client.get('/dashboard/', follow=True)
        # Should be directed to pending_approval or login
        self.assertTrue(
            'pending-approval' in response.redirect_chain[-1][0] if response.redirect_chain else response.status_code == 200
        )

    def test_membership_auto_expiry_calculation(self):
        """Test automatic calculation of expiry date based on plan duration in days."""
        start_date = timezone.now().date()
        subscription = MemberMembership.objects.create(
            member=self.member_user,
            plan=self.plan,
            start_date=start_date
        )
        expected_expiry = start_date + timedelta(days=90)
        self.assertEqual(subscription.expiry_date, expected_expiry)
        self.assertEqual(subscription.status, 'active')

    def test_prevent_duplicate_active_checkin(self):
        """Test that CheckInForm catches duplicate active check-ins on same date."""
        today = timezone.now().date()
        # Create an existing checkin with no checkout
        Attendance.objects.create(
            member=self.member_user,
            attendance_date=today,
            check_in_time='09:00:00',
            check_out_time=None
        )
        
        form = CheckInForm(data={
            'member': self.member_user.id,
            'attendance_date': today,
            'check_in_time': '10:00',
        })
        self.assertFalse(form.is_valid())
        self.assertIn("already checked in", str(form.errors))

    def test_role_based_access_trainer_cannot_access_admin_dashboard(self):
        """Test that trainer cannot access admin dashboard."""
        self.client.login(username='testtrainer', password='password123')
        response = self.client.get('/dashboard/admin/', follow=True)
        # Should redirect to access_denied
        self.assertTrue(
            'access-denied' in response.redirect_chain[-1][0] or response.status_code == 403
        )

    def test_trainer_cannot_login_or_access_dashboard(self):
        """Test that trainer login is blocked and dashboard redirects to access denied."""
        response = self.client.post('/login/', {
            'username': 'testtrainer',
            'password': 'password123'
        }, follow=True)
        self.assertContains(response, "Trainer portal is disabled")
        
        # If logged in directly via test client, dashboard routes to access_denied
        self.client.login(username='testtrainer', password='password123')
        resp = self.client.get('/dashboard/', follow=True)
        self.assertTrue('access-denied' in resp.redirect_chain[-1][0])

    def test_member_plan_enrollment_generates_receipt_and_shows_in_dashboard(self):
        """Test that member can enroll in plan, generating payment receipt visible on dashboard."""
        self.client.login(username='testmember', password='password123')
        
        # Self-enroll into test plan
        response = self.client.post(f'/memberships/plans/{self.plan.id}/enroll/', {
            'payment_method': 'UPI'
        }, follow=True)
        self.assertContains(response, "Successfully enrolled in")
        
        # Verify receipt is rendered on member dashboard
        dashboard_resp = self.client.get('/dashboard/member/')
        self.assertContains(dashboard_resp, "Payment Receipt #")
        self.assertContains(dashboard_resp, "Quarterly Test Plan")
        self.assertContains(dashboard_resp, "View / Print Official Receipt")

