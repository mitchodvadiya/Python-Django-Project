# Gym Management System

A simple gym management website made with Python and Django. It helps a gym manage members, trainers, memberships, payments, attendance, and workout plans.

## What it can do

- Register users and let an admin approve accounts
- Manage members
- Create membership plans and track renewals
- Record payments
- Track member attendance
- Create workout plans
- View reports

## What you need

- Python 3
- pip

## Run the project on Windows

Open PowerShell in the project folder and run:

```powershell
# Optional: create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install Django
pip install -r requirements.txt

# Set up the database
python manage.py migrate

# Add sample users and gym data
python manage.py seed_data

# Start the website
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

## Demo accounts

Run `python manage.py seed_data` before using these accounts.
The admin account is also assigned as the trainer in the sample data, so you do not need a separate trainer account.

| Role | Username | Password |
| --- | --- | --- |
| Admin and trainer | `admin` | `admin123` |
| Member | `member_amit` | `member123` |

The seed command also adds sample membership, payment, attendance, and workout data.

## Run tests

```powershell
python manage.py test
```

The SQLite database is created locally when you run migrations. It is not included in Git.
