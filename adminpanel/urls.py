from django.urls import path
from . import views

app_name = 'adminpanel'

urlpatterns = [
    path('superadmin/', views.superadmin_dashboard, name='superadmin_dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('manage-admins/', views.manage_admins, name='manage_admins'),
    path('manage-tasks/', views.manage_tasks, name='manage_tasks'),
    path('task-reports/', views.task_reports, name='task_reports'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('edit-task/<int:task_id>/', views.edit_task, name='edit_task'),
    path('delete-task/<int:task_id>/', views.delete_task, name='delete_task'),
    path('add-task/', views.add_task, name='add_task'),
    path('assign-user-to-admin/', views.assign_user_to_admin, name='assign_user_to_admin'),
    path('create-admin/', views.create_admin, name='create_admin'),
    path('create-user/', views.create_user, name='create_user'),
]
