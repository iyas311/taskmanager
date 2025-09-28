# Task Management App

Django + DRF + JWT with a custom Admin Panel.

## Install
- Python 3.12+
- Create venv (optional) and install:
  - pip install -r requirements.txt
- Migrate DB:
  - python manage.py makemigrations
  - python manage.py migrate

## Run
- Start server:
  - python manage.py runserver
- Open:
  - http://127.0.0.1:8000/

## Auth (JWT)
- POST /api/login/ → returns { refresh, access }
- POST /api/token/refresh/ → returns { access }
- Use on protected routes:
  - Authorization: Bearer <ACCESS_TOKEN>
- Lifetimes:
  - Access: 1 hour
  - Refresh: 14 days

## API Endpoints
- GET /api/tasks/
  - Returns tasks for the authenticated user only.
- PUT /api/tasks/{id}/
  - Allowed: status, completion_report, worked_hours (positive).
  - If status=completed: completion_report and worked_hours are required.
- GET /api/tasks/{id}/report/
  - Auth: Admin or SuperAdmin
  - SuperAdmin: any completed task
  - Admin: completed tasks if they manage the user OR they assigned the task.

## Admin Panel (Web UI)
- /adminpanel/superadmin/
- /adminpanel/admin/
- /adminpanel/manage-users/
- /adminpanel/manage-admins/
- /adminpanel/manage-tasks/
- /adminpanel/task-reports/

# Project Structure (key)
- core/settings.py  – settings, REST/JWT
- core/urls.py  – routes for accounts, adminpanel, api
- accounts/  – custom user (role , assigned_admin )
- tasks/  – Task model, API views/serializers
- adminpanel/  – Web UI views/urls/templates
- core/templates/base.html  – base template