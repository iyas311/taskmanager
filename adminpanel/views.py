from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from core.forms import UserEditForm, TaskEditForm, TaskCreateForm, AssignUserToAdminForm
from accounts.models import User
from tasks.models import Task
from django.http import HttpResponseForbidden
from django.urls import reverse
from django.core.exceptions import ValidationError

@login_required
def create_admin(request):
    if not is_superadmin(request.user):
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = UserEditForm(request.POST)
        # Do not show/accept assigned_admin when creating an admin
        if 'assigned_admin' in form.fields:
            form.fields.pop('assigned_admin')
        if form.is_valid():
            admin = form.save(commit=False)
            admin.role = 'admin'
            admin.set_password(request.POST.get('password'))
            admin.save()
            messages.success(request, 'Admin created successfully.')
            return redirect(reverse('adminpanel:manage_admins'))
    else:
        form = UserEditForm()
        # Remove assigned_admin field from admin creation form
        if 'assigned_admin' in form.fields:
            form.fields.pop('assigned_admin')
    return render(request, 'adminpanel/create_admin.html', {'form': form})

@login_required
def create_user(request):
    if not is_superadmin(request.user):
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = UserEditForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Default role to 'user' if not provided
            if not getattr(user, 'role', None):
                user.role = 'user'
            password = request.POST.get('password')
            if password:
                user.set_password(password)
            user.save()
            messages.success(request, 'User created successfully.')
            return redirect('adminpanel:manage_users')
    else:
        form = UserEditForm()
    return render(request, 'adminpanel/create_user.html', {'form': form})

@login_required
def assign_user_to_admin(request):
    if not is_superadmin(request.user):
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = AssignUserToAdminForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            admin = form.cleaned_data['admin']
            user.assigned_admin = admin
            user.save()
            messages.success(request, f'User {user.username} assigned to admin {admin.username}.')
            return redirect(reverse('adminpanel:manage_users'))
    else:
        form = AssignUserToAdminForm()
    return render(request, 'adminpanel/assign_user_to_admin.html', {'form': form})

# Admin or SuperAdmin: Add task
@login_required
def add_task(request):
    if not (is_superadmin(request.user) or is_admin(request.user)):
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = TaskCreateForm(request.POST)
        # Limit assignable users for admins to only their users
        if is_admin(request.user):
            form.fields['assigned_to'].queryset = User.objects.filter(role='user', assigned_admin=request.user)
        else:
            form.fields['assigned_to'].queryset = User.objects.filter(role='user')
        if form.is_valid():
            task = form.save(commit=False)
            # Record who assigned the task (admin or superadmin)
            task.assigned_by = request.user
            try:
                task.full_clean()
                task.save()
                messages.success(request, 'Task created successfully.')
                return redirect('adminpanel:manage_tasks')
            except ValidationError as e:
                # Attach validation errors to the form so they render nicely
                for field, errors in e.message_dict.items():
                    for err in errors:
                        if field in form.fields:
                            form.add_error(field, err)
                        else:
                            form.add_error(None, err)
    else:
        form = TaskCreateForm()
        if is_admin(request.user):
            form.fields['assigned_to'].queryset = User.objects.filter(role='user', assigned_admin=request.user)
        else:
            form.fields['assigned_to'].queryset = User.objects.filter(role='user')
    return render(request, 'adminpanel/add_task.html', {'form': form})

# SuperAdmin: Edit user
@login_required
def edit_user(request, user_id):
    if not is_superadmin(request.user):
        return HttpResponseForbidden()
    user = get_object_or_404(User, id=user_id)
    admins = User.objects.filter(role='admin')
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        # Only allow assigning an admin for regular users
        if user.role != 'user' and 'assigned_admin' in form.fields:
            form.fields.pop('assigned_admin')
        assigned_admin_id = request.POST.get('assigned_admin')
        if form.is_valid():
            user = form.save(commit=False)
            if user.role == 'user':
                if assigned_admin_id:
                    user.assigned_admin = User.objects.get(id=assigned_admin_id)
                else:
                    user.assigned_admin = None
            user.save()
            messages.success(request, 'User updated successfully.')
            return redirect('adminpanel:manage_users')
    else:
        form = UserEditForm(instance=user)
        # Only show assigned_admin input for regular users
        if user.role != 'user' and 'assigned_admin' in form.fields:
            form.fields.pop('assigned_admin')
    return render(request, 'adminpanel/edit_user.html', {'form': form, 'user_obj': user, 'admins': admins})

# SuperAdmin: Delete user
@login_required
def delete_user(request, user_id):
    if not is_superadmin(request.user):
        return HttpResponseForbidden()
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        # Prevent deleting an admin who still has assigned users
        if user.role == 'admin' and user.assigned_users.exists():
            messages.error(request, 'Cannot delete this admin until their assigned users are reassigned or removed.')
            return redirect('adminpanel:manage_admins')
        user.delete()
        messages.success(request, 'User deleted successfully.')
        return redirect('adminpanel:manage_users')
    return render(request, 'adminpanel/delete_user.html', {'user_obj': user})

# SuperAdmin/Admin: Edit task
@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    # Only SuperAdmin or Admin editing their own users' tasks
    if is_superadmin(request.user) or (is_admin(request.user) and getattr(task.assigned_to, 'assigned_admin_id', None) == request.user.id):
        if request.method == 'POST':
            form = TaskEditForm(request.POST, instance=task)
            # Limit assignable users for admins to only their users
            if is_admin(request.user):
                form.fields['assigned_to'].queryset = User.objects.filter(role='user', assigned_admin=request.user)
            else:
                form.fields['assigned_to'].queryset = User.objects.filter(role='user')
            if form.is_valid():
                task = form.save(commit=False)
                try:
                    task.full_clean()
                    task.save()
                    messages.success(request, 'Task updated successfully.')
                    return redirect('adminpanel:manage_tasks')
                except ValidationError as e:
                    for field, errors in e.message_dict.items():
                        for err in errors:
                            if field in form.fields:
                                form.add_error(field, err)
                            else:
                                form.add_error(None, err)
        else:
            form = TaskEditForm(instance=task)
            if is_admin(request.user):
                form.fields['assigned_to'].queryset = User.objects.filter(role='user', assigned_admin=request.user)
            else:
                form.fields['assigned_to'].queryset = User.objects.filter(role='user')
        return render(request, 'adminpanel/edit_task.html', {'form': form, 'task': task})
    return HttpResponseForbidden()

# SuperAdmin/Admin: Delete task
@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    # Only SuperAdmin or Admin deleting their own users' tasks
    if is_superadmin(request.user) or (is_admin(request.user) and getattr(task.assigned_to, 'assigned_admin_id', None) == request.user.id):
        if request.method == 'POST':
            task.delete()
            messages.success(request, 'Task deleted successfully.')
            return redirect('adminpanel:manage_tasks')
        return render(request, 'adminpanel/delete_task.html', {'task': task})
    return HttpResponseForbidden()


def is_superadmin(user):
    return user.is_authenticated and user.role == 'superadmin'


def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

@login_required
def superadmin_dashboard(request):
    if not is_superadmin(request.user):
        return HttpResponseForbidden()
    return render(request, 'adminpanel/superadmin_dashboard.html')

@login_required
def admin_dashboard(request):
    if not is_admin(request.user):
        return HttpResponseForbidden()
    return render(request, 'adminpanel/admin_dashboard.html')

@login_required
def manage_users(request):
    if not is_superadmin(request.user):
        return HttpResponseForbidden()
    users = User.objects.filter(role='user')
    return render(request, 'adminpanel/manage_users.html', {'users': users})

@login_required
def manage_admins(request):
    if not is_superadmin(request.user):
        return HttpResponseForbidden()
    admins = (User.objects
              .filter(role='admin')
              .prefetch_related('assigned_users')
              .order_by('username'))
    return render(request, 'adminpanel/manage_admins.html', {'admins': admins})

@login_required
def manage_tasks(request):
    if is_superadmin(request.user):
        tasks = Task.objects.all()
    elif is_admin(request.user):
        # Admins can only view tasks for their own users
        tasks = Task.objects.filter(assigned_to__assigned_admin=request.user)
    else:
        return HttpResponseForbidden()
    return render(request, 'adminpanel/manage_tasks.html', {'tasks': tasks})

@login_required
def task_reports(request):
    if is_superadmin(request.user):
        reports = Task.objects.filter(status='completed')
    elif is_admin(request.user):
        # Admins can only view reports for their own users
        reports = Task.objects.filter(status='completed', assigned_to__assigned_admin=request.user)
    else:
        return HttpResponseForbidden()
    return render(request, 'adminpanel/task_reports.html', {'reports': reports})
