"""
Management command to populate database with demo users, roles, plans, memberships, payments, attendance, and workouts.
Usage: python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from accounts.models import UserProfile
from members.models import Member
from memberships.models import MembershipPlan, MemberMembership
from payments.models import Payment
from attendance.models import Attendance
from workouts.models import WorkoutPlan

class Command(BaseCommand):
    help = 'Populates the database with initial demonstration data for viva and practical examination.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding Gym Management System data...")

        # 1. Administrator Account (Admin & Coach)
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@gymsystem.local',
                'first_name': 'Gym',
                'last_name': 'Administrator',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password('admin123')
        admin_user.save()
        UserProfile.objects.update_or_create(
            user=admin_user,
            defaults={
                'role': 'admin',
                'status': 'approved',
                'phone': '9876543210',
                'address': 'Fitness Club, Main Road, Rajkot',
                'specialization': 'Head Coach & General Fitness',
            }
        )
        self.stdout.write(self.style.SUCCESS("Administrator & Trainer: admin / admin123"))

        # 4. Approved Member 1
        member_user1, _ = User.objects.get_or_create(
            username='member_amit',
            defaults={
                'email': 'amit.patel@example.com',
                'first_name': 'Amit',
                'last_name': 'Patel',
            }
        )
        member_user1.set_password('member123')
        member_user1.save()
        UserProfile.objects.update_or_create(
            user=member_user1,
            defaults={
                'role': 'member',
                'status': 'approved',
                'phone': '9900112233',
                'address': 'Kotecha Chowk, Rajkot',
            }
        )
        member_rec1, _ = Member.objects.update_or_create(
            user=member_user1,
            defaults={
                'phone': '9900112233',
                'address': 'Kotecha Chowk, Rajkot',
                'assigned_trainer': admin_user,
            }
        )
        self.stdout.write(self.style.SUCCESS("Approved Member: member_amit / member123"))

        # 5. Approved Member 2
        member_user2, _ = User.objects.get_or_create(
            username='member_priya',
            defaults={
                'email': 'priya.joshi@gmail.com',
                'first_name': 'Priya',
                'last_name': 'Joshi',
            }
        )
        member_user2.set_password('member123')
        member_user2.save()
        UserProfile.objects.update_or_create(
            user=member_user2,
            defaults={
                'role': 'member',
                'status': 'approved',
                'phone': '9988776655',
                'address': 'Kalawad Road, Rajkot',
            }
        )
        member_rec2, _ = Member.objects.update_or_create(
            user=member_user2,
            defaults={
                'phone': '9988776655',
                'address': 'Kalawad Road, Rajkot',
                'assigned_trainer': admin_user,
            }
        )
        self.stdout.write(self.style.SUCCESS("Approved Member: member_priya / member123"))

        # 6. Pending Member
        member_user3, _ = User.objects.get_or_create(
            username='member_rohit',
            defaults={
                'email': 'rohit.verma@gmail.com',
                'first_name': 'Rohit',
                'last_name': 'Verma',
            }
        )
        member_user3.set_password('member123')
        member_user3.save()
        UserProfile.objects.update_or_create(
            user=member_user3,
            defaults={
                'role': 'member',
                'status': 'pending',
                'phone': '9711223344',
                'address': '150 Feet Ring Road, Rajkot',
            }
        )
        Member.objects.update_or_create(
            user=member_user3,
            defaults={
                'phone': '9711223344',
                'address': '150 Feet Ring Road, Rajkot',
            }
        )
        self.stdout.write(self.style.WARNING("Pending Member: member_rohit / member123"))

        # 7. Membership Plans
        plan_monthly, _ = MembershipPlan.objects.update_or_create(
            name='Monthly Plan',
            defaults={
                'duration_days': 30,
                'price': 1500.00,
                'description': 'Full gym access including cardio and strength machines for 1 month.',
            }
        )
        plan_quarterly, _ = MembershipPlan.objects.update_or_create(
            name='Quarterly Plan',
            defaults={
                'duration_days': 90,
                'price': 4000.00,
                'description': 'Quarterly gym package with free initial fitness assessment and locker access.',
            }
        )
        plan_halfyearly, _ = MembershipPlan.objects.update_or_create(
            name='Half-Yearly Plan',
            defaults={
                'duration_days': 180,
                'price': 7500.00,
                'description': '6 months comprehensive gym membership with steam bath and diet guidance.',
            }
        )
        plan_yearly, _ = MembershipPlan.objects.update_or_create(
            name='Yearly Plan',
            defaults={
                'duration_days': 365,
                'price': 13500.00,
                'description': 'Annual all-inclusive VIP pass with 2 complimentary personal trainer sessions.',
            }
        )
        self.stdout.write(self.style.SUCCESS("Membership Plans seeded."))

        # 8. Active and Expired Subscriptions
        today = timezone.now().date()
        # Amit: Active Quarterly Plan (started 10 days ago)
        amit_membership, _ = MemberMembership.objects.update_or_create(
            member=member_user1,
            plan=plan_quarterly,
            defaults={
                'start_date': today - timedelta(days=10),
                'expiry_date': today - timedelta(days=10) + timedelta(days=90),
                'status': 'active',
            }
        )
        # Priya: Expired Monthly Plan (started 45 days ago, expired 15 days ago)
        priya_membership, _ = MemberMembership.objects.update_or_create(
            member=member_user2,
            plan=plan_monthly,
            defaults={
                'start_date': today - timedelta(days=45),
                'expiry_date': today - timedelta(days=15),
                'status': 'expired',
            }
        )
        self.stdout.write(self.style.SUCCESS("Member Subscriptions seeded."))

        # 9. Payments
        Payment.objects.update_or_create(
            member=member_user1,
            membership=amit_membership,
            defaults={
                'amount': 4000.00,
                'payment_date': today - timedelta(days=10),
                'payment_method': 'UPI',
                'payment_status': 'Paid',
                'notes': 'Quarterly fee received via GPay.',
            }
        )
        Payment.objects.update_or_create(
            member=member_user2,
            membership=priya_membership,
            defaults={
                'amount': 1500.00,
                'payment_date': today - timedelta(days=45),
                'payment_method': 'Cash',
                'payment_status': 'Paid',
                'notes': 'Monthly fee received in cash at reception.',
            }
        )
        Payment.objects.get_or_create(
            member=member_user2,
            amount=500.00,
            payment_date=today,
            defaults={
                'payment_method': 'UPI',
                'payment_status': 'Pending',
                'notes': 'Personal training addon fee pending verification.',
            }
        )
        self.stdout.write(self.style.SUCCESS("Payments seeded."))

        # 10. Attendance
        Attendance.objects.get_or_create(
            member=member_user1,
            attendance_date=today,
            defaults={
                'check_in_time': '07:30:00',
                'check_out_time': '08:45:00',
            }
        )
        Attendance.objects.get_or_create(
            member=member_user2,
            attendance_date=today,
            defaults={
                'check_in_time': '08:15:00',
                'check_out_time': None, # Currently active inside gym
            }
        )
        self.stdout.write(self.style.SUCCESS("Attendance records seeded."))

        # 11. Workout Plans for Amit
        WorkoutPlan.objects.update_or_create(
            member=member_user1,
            exercise_name='Barbell Bench Press',
            workout_day='Monday',
            defaults={
                'assigned_trainer': admin_user,
                'sets': 4,
                'repetitions': '10-12 reps',
                'instructions': 'Keep shoulder blades retracted and lower bar with control.',
            }
        )
        WorkoutPlan.objects.update_or_create(
            member=member_user1,
            exercise_name='Incline Dumbbell Press',
            workout_day='Monday',
            defaults={
                'assigned_trainer': admin_user,
                'sets': 3,
                'repetitions': '12 reps',
                'instructions': 'Bench at 30 degree incline, full range of motion.',
            }
        )
        WorkoutPlan.objects.update_or_create(
            member=member_user1,
            exercise_name='Lat Pulldown',
            workout_day='Wednesday',
            defaults={
                'assigned_trainer': admin_user,
                'sets': 4,
                'repetitions': '12 reps',
                'instructions': 'Pull to upper chest, squeeze lats at contraction.',
            }
        )
        WorkoutPlan.objects.update_or_create(
            member=member_user1,
            exercise_name='Barbell Squats',
            workout_day='Friday',
            defaults={
                'assigned_trainer': admin_user,
                'sets': 4,
                'repetitions': '8-10 reps',
                'instructions': 'Break parallel with thighs, keep chest upright.',
            }
        )
        self.stdout.write(self.style.SUCCESS("Workout Plans seeded."))

        self.stdout.write(self.style.SUCCESS("\nAll demo data seeded successfully!"))
