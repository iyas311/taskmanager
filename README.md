# Task Management App

A Django app with JWT-authenticated APIs and a custom Admin Panel for SuperAdmins/Admins.

## Quick Start
- Python 3.12+
- Create/activate venv, install deps:
```bash
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
- Open: http://127.0.0.1:8000/

## Auth (JWT)
- Access token lifetime: 1 hour
- Refresh token lifetime: 14 days

Endpoints:
- POST `/api/login/` → {"refresh", "access"}
- POST `/api/token/refresh/` → {"access"}

Use header on protected routes:
```
Authorization: Bearer <ACCESS_TOKEN>
```

## Admin Panel (Web UI)
- SuperAdmin Dashboard: `/adminpanel/superadmin/`
- Admin Dashboard: `/adminpanel/admin/`
- Manage Users: `/adminpanel/manage-users/`
- Manage Admins: `/adminpanel/manage-admins/`
- Manage Tasks: `/adminpanel/manage-tasks/`
- Task Reports: `/adminpanel/task-reports/`

Behavior:
- SuperAdmin: manage everything (admins, users, all tasks & reports).
- Admin: manage tasks for their own users.
- Reports: Admin can view a completed task if they either manage the user or personally assigned the task.

## API (User-facing)
Base: `/api/`

- GET `/api/tasks/`
  - Returns only the authenticated user’s tasks.

- PUT `/api/tasks/{id}/`
  - Allowed fields: `status`, `completion_report`, `worked_hours` (positive number)
  - If `status = "completed"`, `completion_report` and `worked_hours` are required.

- GET `/api/tasks/{id}/report/`
  - Auth: Admin or SuperAdmin
  - SuperAdmin: any completed task
  - Admin: completed tasks for users they manage OR tasks they assigned

## Curl examples
Login:
```bash
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"<USER>","password":"<PASS>"}'
```
Get my tasks:
```bash
curl -X GET http://127.0.0.1:8000/api/tasks/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```
Complete a task (PUT):
```bash
curl -X PUT http://127.0.0.1:8000/api/tasks/5/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"status":"completed","completion_report":"Did X,Y,Z","worked_hours":2.5}'
```
Get report (Admin/SuperAdmin):
```bash
curl -X GET http://127.0.0.1:8000/api/tasks/5/report/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

## Roles
- SuperAdmin: manage admins/users, all tasks, all reports.
- Admin: manage tasks for their users; view reports they manage or assigned.
- User: view/update own tasks.

## Project Structure (key)
- `core/settings.py` – settings, REST/JWT
- `core/urls.py` – routes for accounts, adminpanel, api
- `accounts/` – custom user (`role`, `assigned_admin`)
- `tasks/` – Task model, API views/serializers
- `adminpanel/` – Web UI views/urls/templates
- `core/templates/base.html` – base template

## Notes
- Model-level validation prevents completing a task without `completion_report` and positive `worked_hours` (enforced everywhere: API, Admin Panel, Django Admin).
- Use `createsuperuser` to access Django Admin: `/admin/`.
