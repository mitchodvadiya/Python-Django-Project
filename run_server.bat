@echo off
title Gym Management System - Server
color 0A
echo ========================================================
echo   Starting Gym Management System (Python Django)
echo ========================================================
echo.

cd /d "%~dp0"

echo [1/3] Applying database migrations...
python manage.py migrate
if %ERRORLEVEL% NEQ 0 (
    echo Error during migration! Check Python and Django installation.
    pause
    exit /b %ERRORLEVEL%
)

echo [2/3] Seeding demo accounts (Admin, Trainers, Members)...
python manage.py seed_data

echo [3/3] Opening browser and launching Django development server...
start http://127.0.0.1:8000/
echo.
echo Server running at http://127.0.0.1:8000/
echo Press CTRL+C in this window to stop the server.
echo ========================================================
echo.
python manage.py runserver
pause
