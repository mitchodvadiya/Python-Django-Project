# Gym Management System (Python Django)
### Academic Project for Python Framework (Skill Course)
**Faculty of Engineering & Technology | Department of Information & Communication Technology**  
**Marwadi University, Rajkot, Gujarat**

---

## 1. Project Overview

The **Gym Management System** is a robust, database-driven web application developed in Python using the Django Web Framework. Designed to automate and streamline core gym operations, the application implements:
- **Role-Based Access Control (RBAC):** Distinct interfaces and capabilities for **Administrator**, **Trainer**, and **Member**.
- **User Registration & Approval Workflow:** Public registrants (Members/Trainers) are queued in a *Pending Approval* state and cannot access system services until vetted and authorized by the Gym Administrator.
- **Member & Trainer Management:** Full CRUD operations, trainer assignments, and profile updates.
- **Membership Plans & Subscription Tracking:** Automatic expiration calculations (Python `datetime` / `timedelta`), active vs. expired status tracking, and plan renewals.
- **Financial Payment Ledger:** Recording of membership fee collections (Cash, UPI, Card, Net Banking) and tracking of outstanding balances.
- **Attendance Tracking:** Daily member check-in and checkout logging with server-side validation preventing duplicate active check-ins.
- **Workout Plan Management:** Weekly exercise schedules (sets, repetitions, instructions) assigned by trainers to members.
- **Official HTML System Reports:** Tabular audits across members, trainers, pending approvals, memberships, finances, attendances, and workout splits.

---

## 2. Technology Stack & Architectural Constraints

In strict accordance with academic guidelines:
* **Backend:** Python 3.x
* **Framework:** Django 4.x / 5.x (Model-View-Template Architecture)
* **Database:** SQLite3 (`db.sqlite3` with Django ORM)
* **Frontend:** Semantic Plain HTML & Django Template Language (DTL)
* **Styling & Scripting Policy:** **Zero CSS** (no inline styles, `<style>` tags, or external CSS) and **Zero JavaScript** (no `<script>` tags, third-party libraries, or UI frameworks). All functionality is rendered and validated purely through standard HTML elements (`<table>`, `<form>`, `<input>`, `<a>`, `<p>`) and server-side Django processing.

---

## 3. Quickstart & Local Setup Guide (Windows PowerShell)

Open PowerShell and navigate to the project directory:

```powershell
# 1. Navigate to the project folder
cd "d:\SEM_5\Python Django\Gym_Mangement_System"

# 2. (Optional) Create and activate a Python virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install project dependencies
pip install -r requirements.txt

# 4. Apply the checked-in migrations to create the SQLite database
python manage.py migrate

# 5. Populate the local database with demo users, plans, and records
python manage.py seed_data

# 6. (Optional) Run automated unit tests to verify system integrity
python manage.py test

# 7. Start the Django development server
python manage.py runserver
```

The local SQLite database and Python cache/virtual-environment files are excluded from Git. Run the migration and seed commands above to create a local demo database.

Once running, access the web application in any browser:
* **Web Portal:** `http://127.0.0.1:8000/`
* **Django Admin Site:** `http://127.0.0.1:8000/admin/`

---

## 4. Pre-configured Credentials for Viva Voce Demonstration

The command `python manage.py seed_data` creates the following demonstration accounts:

| Role | Username | Password | Status | Intended Demonstration |
| :--- | :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `admin123` | Approved (Superuser) | Has full access: view statistics, approve/reject accounts, manage members/trainers/plans, record payments, and inspect reports. |
| **Trainer** | `trainer_rahul` | `trainer123` | Approved | Views assigned members (`Amit Patel`) and assigns/modifies weekly workout routines. |
| **Member** | `member_amit` | `member123` | Approved | Has an **Active Quarterly Membership Plan**, assigned trainer, payment history, and workout schedule. |
| **Member (Expired)** | `member_priya` | `member123` | Approved | Has an **Expired Monthly Membership Plan** to demonstrate renewal and expiration handling. |
| **Pending Member** | `member_rohit` | `member123` | Pending Approval | Demonstrates the approval gatekeeper (cannot log in until administrator approves). |
| **Pending Trainer** | `trainer_sneha` | `trainer123` | Pending Approval | Demonstrates trainer verification workflow. |

---

## 5. Project Architecture & Modular Structure

The project follows a clean, decoupled Django application layout:

```text
Gym_Mangement_System/
│
├── manage.py                          # Django CLI utility
├── db.sqlite3                         # SQLite database instance
│
├── gym_system/                        # Root Project Configuration
│   ├── settings.py                    # Installed apps, DTL, SQLite, and timezone config
│   ├── urls.py                        # Master URL router
│   ├── wsgi.py                        # Web Server Gateway Interface
│   └── asgi.py                        # Asynchronous Server Gateway Interface
│
├── accounts/                          # Module 1 & 2: Auth, Approvals & Dashboards
│   ├── models.py                      # UserProfile (role, status, phone, address)
│   ├── views.py                       # Login, register, logout, admin/trainer/member dashboards
│   ├── forms.py                       # Registration, Login, and Status update forms
│   ├── decorators.py                  # @admin_required, @trainer_required, @member_required
│   ├── urls.py                        # Routing for auth and approval endpoints
│   └── management/commands/seed_data.py # Data seeding management command
│
├── members/                           # Module 3: Member Management
│   ├── models.py                      # Member model (links to User, trainer assignment)
│   ├── views.py                       # Member CRUD, search, trainer/plan assignment
│   ├── forms.py                       # Member creation and edit forms
│   └── urls.py                        # /members/ routing
│
├── trainers/                          # Module 4: Trainer Management
│   ├── models.py                      # Trainer model (specialization, phone)
│   ├── views.py                       # Trainer CRUD and assigned members view
│   ├── forms.py                       # Trainer forms
│   └── urls.py                        # /trainers/ routing
│
├── memberships/                       # Module 5: Membership Management
│   ├── models.py                      # MembershipPlan & MemberMembership (with auto-expiry)
│   ├── views.py                       # Plan creation, subscription assignment, renewals
│   ├── forms.py                       # Plan and assignment forms
│   └── urls.py                        # /memberships/ routing
│
├── payments/                          # Module 6: Payment Management
│   ├── models.py                      # Payment model (amount, mode, status, receipt)
│   ├── views.py                       # Record payment, ledger view, collection totals
│   ├── forms.py                       # Payment entry form
│   └── urls.py                        # /payments/ routing
│
├── attendance/                        # Module 7: Attendance Management
│   ├── models.py                      # Attendance model (date, check-in, check-out)
│   ├── views.py                       # Daily log, check-in/out, correction, member history
│   ├── forms.py                       # Check-in form (duplicate prevention validation)
│   └── urls.py                        # /attendance/ routing
│
├── workouts/                          # Module 8: Workout Management
│   ├── models.py                      # WorkoutPlan (day, exercise, sets, reps, instructions)
│   ├── views.py                       # Trainer workout builder & member read-only schedule
│   ├── forms.py                       # Workout form with role-based member filtering
│   └── urls.py                        # /workouts/ routing
│
├── reports/                           # Module 9: Reports
│   ├── views.py                       # Comprehensive tabular reports
│   └── urls.py                        # /reports/ routing
│
└── templates/                         # Plain HTML & DTL Templates
    ├── base.html                      # Root layout, role-based navigation, flash alerts
    ├── accounts/                      # login, register, dashboards, approvals
    ├── members/                       # lists, details, forms, deletion confirmation
    ├── trainers/                      # rosters, details, assigned members
    ├── memberships/                   # plans, subscriptions, renewals
    ├── payments/                      # payment ledger, receipts
    ├── attendance/                    # daily logs, check-in, checkout
    ├── workouts/                      # workout tables, member weekly split
    └── reports/                       # 7 distinct system reports in HTML tables
```

---

## 6. Database Entity-Relationship (ER) Schema

```
+--------------------+            +------------------------+
|  auth_user (Core)  | 1 <-----> 1 |  accounts_userprofile  |
+--------------------+            +------------------------+
| id (PK)            |            | user_id (FK, Unique)   |
| username           |            | role (admin/trainer/..) |
| password (hashed)  |            | status (approved/..)   |
| email              |            | phone, address         |
+--------------------+            +------------------------+
        | 1                                 |
        |                                   |
        +---------------+-------------------+
        | 1             | 1                 | 1
        v               v                   v
+------------------+ +-----------------+ +-------------------------+
|  members_member  | | trainers_trainer| | memberships_membershipplan |
+------------------+ +-----------------+ +-------------------------+
| id (PK)          | | id (PK)         | | id (PK)                 |
| user_id (FK)     | | user_id (FK)    | | name (Monthly, Yearly)  |
| assigned_trainer | | specialization  | | duration_days (30, 365) |
| phone, address   | | phone           | | price                   |
+------------------+ +-----------------+ +-------------------------+
        | 1                     ^                   | 1
        |                       |                   |
        v *                     |                   v *
+-----------------------------------+   +--------------------------+
|  memberships_membermembership     |   |    payments_payment      |
+-----------------------------------+   +--------------------------+
| id (PK)                           |   | id (PK)                  |
| member_id (FK -> User)            |   | member_id (FK -> User)   |
| plan_id (FK -> MembershipPlan)    |   | membership_id (FK, Null) |
| start_date, expiry_date           |   | amount, payment_date     |
| status (active / expired)         |   | method (Cash/UPI/Card)   |
+-----------------------------------+   | payment_status (Paid/..) |
        | 1                             +--------------------------+
        |
        +-----------------------+
        | *                     | *
        v                       v
+------------------------+  +-------------------------------+
| attendance_attendance  |  |     workouts_workoutplan      |
+------------------------+  +-------------------------------+
| id (PK)                |  | id (PK)                       |
| member_id (FK -> User) |  | member_id (FK -> User)        |
| attendance_date        |  | assigned_trainer_id (FK)      |
| check_in_time          |  | workout_day (Mon, Tue, etc.)  |
| check_out_time         |  | exercise_name, sets, reps     |
+------------------------+  +-------------------------------+
```

---

## 7. Syllabus Topics & Viva Voce Q&A Preparation

### Q1: What is the MVT architecture in Django, and how is it used in this project?
**Answer:**  
MVT stands for **Model-View-Template**:
* **Model (`models.py`):** The data layer that defines database tables, fields, and constraints using Django's ORM (e.g., `Member`, `MembershipPlan`, `Payment`).
* **View (`views.py`):** The business logic layer that handles HTTP requests, interacts with models, processes forms, enforces role checks, and passes context dictionaries to templates.
* **Template (`templates/*.html`):** The presentation layer written in HTML and Django Template Language (DTL) that dynamically renders data using tags like `{% for %}`, `{% if %}`, and `{{ variable }}`.

### Q2: How does the User Registration Approval Workflow work?
**Answer:**  
1. When a visitor submits the registration form, Django validates the data through `UserRegistrationForm`.
2. A new `User` record is created using `User.objects.create_user()` with a securely hashed password.
3. An associated `UserProfile` is created with `status='pending'` and the chosen role (`member` or `trainer`).
4. Public users are strictly forbidden from creating administrator accounts.
5. Pending users are prevented from logging in; if they attempt login, Django intercepts them and directs them to `pending_approval.html`.
6. The administrator reviews pending requests on `pending_users.html` and approves or rejects them via POST actions. Once approved, `status` updates to `approved` and access is unlocked.

### Q3: How is membership expiration calculated?
**Answer:**  
In `memberships/models.py` and `memberships/views.py`, Python's `datetime.date` and `datetime.timedelta` calculate expiry:
```python
expiry_date = start_date + timedelta(days=plan.duration_days)
```
Whenever views or reports run, Django compares `expiry_date < timezone.now().date()`. If expired, the status is automatically updated to `expired`.

### Q4: How is duplicate active check-in prevented in Attendance?
**Answer:**  
In `attendance/forms.py`, the form's `clean()` method queries the database:
```python
active_checkin = Attendance.objects.filter(
    member=member,
    attendance_date=date,
    check_out_time__isnull=True
).exists()
if active_checkin:
    raise forms.ValidationError("Member is already checked in without a checkout time.")
```
This guarantees an active check-in must have a recorded checkout before another check-in can be created on the same day.

### Q5: How are role permissions enforced on protected views?
**Answer:**  
Using custom Python function decorators in `accounts/decorators.py`:
* `@admin_required`: Checks `request.user.is_authenticated`, verifies `user.profile.role == 'admin'` (or superuser), and checks `status == 'approved'`.
* `@trainer_required`: Verifies the user is an approved trainer.
* `@member_required`: Verifies the user is an approved member.
If an unauthorized user attempts direct URL navigation, they are redirected to `access_denied.html`.

### Q6: Why are passwords not stored as plain text?
**Answer:**  
Django uses salted PBKDF2 with SHA-256 password hashing by default via `User.objects.create_user()`. Even if the database is inspected directly, passwords remain completely irreversible.

---

## 8. Summary of Completed Academic Modules

1. **Module 1 (Authentication):** `login.html`, `register.html`, `pending_approval.html`, `access_denied.html`.
2. **Module 2 (Admin Dashboard):** Real-time statistics, metrics tables, pending requests, and shortcuts.
3. **Module 3 (Member Management):** Member CRUD, name/phone search, trainer assignment, personal detail edits.
4. **Module 4 (Trainer Management):** Trainer CRUD, specialization tracking, assigned member rosters.
5. **Module 5 (Membership Management):** Plans, durations, prices, automated expiry calculation, subscription renewals.
6. **Module 6 (Payment Management):** Recording receipts, tracking Paid vs. Pending balances, total collection aggregates.
7. **Module 7 (Attendance Management):** Check-in, checkout, duplicate prevention, admin corrections, member logs.
8. **Module 8 (Workout Management):** Weekly split scheduling (Monday–Sunday), trainer routine assignments, member view.
9. **Module 9 (Reports):** Tabular reports for members, trainers, pending accounts, subscriptions, payments, attendance, and workouts.
