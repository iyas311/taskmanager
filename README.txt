Task Management Application - Setup and Usage Guide

====================================
1) Prerequisites
====================================
- Windows OS (project paths below use Windows-style paths)
- Python 3.12+ installed and on PATH
- Git Bash or PowerShell/Command Prompt

Project root:
C:/Users/iyas2/OneDrive/Desktop/task

Virtual environment (already present):
C:/Users/iyas2/OneDrive/Desktop/task/.venv


====================================
2) Create/Activate Virtual Environment
====================================
If you need to recreate the venv (optional):
- PowerShell/CMD:
  python -m venv .venv

Activate venv:
- PowerShell:
  .venv\Scripts\Activate.ps1
- CMD:
  .venv\Scripts\activate.bat
- Git Bash:
  source .venv/Scripts/activate


====================================
3) Install Dependencies
====================================
- With the venv active, from project root:
  pip install -r requirements.txt

requirements.txt contains (at least):
- Django>=4.2
- djangorestframework>=3.14
- djangorestframework-simplejwt>=5.2


====================================
4) Database Setup (SQLite)
====================================
- Make and run migrations:
  python manage.py makemigrations
  python manage.py migrate

The default DB is SQLite at:
  db.sqlite3


====================================
5) Run the Development Server
====================================
- From project root with venv active:
  python manage.py runserver

- Alternatively (absolute path to venv python):
  C:/Users/iyas2/OneDrive/Desktop/task/.venv/Scripts/python.exe manage.py runserver

- Visit in browser:
  http://127.0.0.1:8000/

JWT lifetimes (configured in core/settings.py):
- Access token: 1 hour
- Refresh token: 14 days


====================================
6) Roles and Default Accounts
====================================
Custom user model with roles: superadmin, admin, user

Example accounts used during development/testing:
- SuperAdmin: username: iyas, password: 123
- User:       username: iyas3, password: Iy@s2458

If you need to create a superuser account:
  python manage.py createsuperuser


====================================
7) Admin Panel (Custom)
====================================
Custom Admin Panel URLs:
- SuperAdmin Dashboard:  http://127.0.0.1:8000/adminpanel/superadmin/
- Admin Dashboard:      http://127.0.0.1:8000/adminpanel/admin/

Main pages:
- Manage Users:          /adminpanel/manage-users/
- Manage Admins:         /adminpanel/manage-admins/
- Manage Tasks:          /adminpanel/manage-tasks/
- Task Reports:          /adminpanel/task-reports/
- Create New Task:       /adminpanel/add-task/
- Create New Admin:      /adminpanel/create-admin/
- Create New User:       /adminpanel/create-user/
- Assign User to Admin:  /adminpanel/assign-user-to-admin/

Behavior:
- SuperAdmin can manage everything (admins, users, all tasks).
- Admin can create/manage tasks only for their assigned users.
- Task Reports show Completion Report and Worked Hours for completed tasks.
- Admins can view a completed task's report if they either:
  - manage the user (assigned_to.assigned_admin == admin), OR
  - personally assigned the task (task.assigned_by == admin).


====================================
8) Django Admin (Stock)
====================================
Django admin is also available if needed:
  http://127.0.0.1:8000/admin/
Use a superuser created via createsuperuser.


====================================
9) API Endpoints Reference (JWT, DRF)
====================================
Base path for API: /api/

Authentication (JWT via SimpleJWT)
- POST /api/login/
  - Auth: Public
  - Body: {"username":"<user>","password":"<pass>"}
  - Response: {"refresh":"...","access":"..."}

- POST /api/token/refresh/
  - Auth: Public
  - Body: {"refresh":"<YOUR_REFRESH_TOKEN>"}
  - Response: {"access":"<NEW_ACCESS_TOKEN>"}

Usage: Send the access token in all protected requests:
  Authorization: Bearer <ACCESS_TOKEN>

Tasks (User-facing)
- GET /api/tasks/
  - Auth: User
  - Returns only the tasks assigned to the authenticated user.

- PUT /api/tasks/{id}/
  - Auth: User (only for tasks assigned to them)
  - Updates allowed: status, completion_report, worked_hours
  - Rule: If status = "completed", both completion_report and worked_hours are required (worked_hours must be positive).

- GET /api/tasks/{id}/report/
  - Auth: Admin or SuperAdmin
  - SuperAdmin: may view any completed task.
  - Admin: may view completed tasks if they manage the user OR they personally assigned the task.


====================================
10) Example API Calls (curl)
====================================
Login:
  curl -X POST http://127.0.0.1:8000/api/login/ \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"iyas3\",\"password\":\"Iy@s2458\"}"

Refresh:
  curl -X POST http://127.0.0.1:8000/api/token/refresh/ \
    -H "Content-Type: application/json" \
    -d "{\"refresh\":\"<YOUR_REFRESH_TOKEN>\"}"

Get my tasks:
  curl -X GET http://127.0.0.1:8000/api/tasks/ \
    -H "Authorization: Bearer <ACCESS_TOKEN>"

Mark a task completed (requires report + hours) using PUT:
  curl -X PUT http://127.0.0.1:8000/api/tasks/5/ \
    -H "Authorization: Bearer <ACCESS_TOKEN>" \
    -H "Content-Type: application/json" \
    -d "{\"status\":\"completed\",\"completion_report\":\"Did X,Y,Z\",\"worked_hours\":2.5}"

Get report (as admin/superadmin):
  curl -X GET http://127.0.0.1:8000/api/tasks/5/report/ \
    -H "Authorization: Bearer <ACCESS_TOKEN>"


====================================
11) Postman Quick Setup
====================================
Create a collection with:
- Login (POST /api/login/) – capture access, refresh
- Refresh (POST /api/token/refresh/) – use refresh to get new access
- Get My Tasks (GET /api/tasks/) – Authorization: Bearer <access>
- Update Task (PUT /api/tasks/{id}/) – send status, completion_report, worked_hours
- Get Task Report (GET /api/tasks/{id}/report/)

Make sure to set Content-Type: application/json and send raw JSON bodies.


====================================
12) Roles & Permissions Summary
====================================
- SuperAdmin
  - Manage admins and users, assign roles, view all tasks and reports.
- Admin
  - Create/assign/manage tasks, but only for their own users.
  - View completion reports for completed tasks they either manage (user assigned to them) or tasks they assigned themselves.
- User
  - View and update own tasks (status, completion_report, worked_hours).
  - Must provide report and hours when completing a task.


====================================
13) Troubleshooting
====================================
- ModuleNotFoundError: rest_framework_simplejwt
  Run: pip install -r requirements.txt

- sqlite OperationalError: no such column (e.g., assigned_admin_id)
  Run: python manage.py makemigrations && python manage.py migrate

- Git Bash path issues using Windows paths
  Use forward slashes in Git Bash or run from PowerShell/CMD.

- 401 Unauthorized
  Ensure Authorization header: Bearer <ACCESS_TOKEN>. Token not expired.

- 403 / 404 on task updates
  Users can only update their own tasks; admins only see their users.

- Status validation says invalid choice
  Allowed values are: pending, in_progress, completed.


====================================
14) Project Structure (key files)
====================================
- core/settings.py                – Django settings, REST/JWT config, templates dir
- core/urls.py                    – Includes accounts/, adminpanel/, and api/ routes
- tasks/models.py                 – Task model with completion_report, worked_hours
- tasks/serializers.py            – DRF serializers + validation rules
- tasks/views.py                  – JWT login, user tasks list/update, report view
- tasks/urls.py                   – API endpoints + token refresh
- accounts/models.py              – Custom User with role and assigned_admin
- adminpanel/views.py             – Custom admin panel views and permissions
- adminpanel/urls.py              – Admin panel routes
- core/forms.py                   – Forms for admin panel
- adminpanel/templates/adminpanel/* – Admin panel HTML templates


====================================
15) Logout Behavior
====================================
- Logout button in the navbar submits a POST to /accounts/logout/
- After logout, redirect to /accounts/login/


You're ready to go. If you need changes or additional endpoints, see this README for the structure and update accordingly.
