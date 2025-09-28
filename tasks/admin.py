from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
	list_display = ('title', 'assigned_to', 'status', 'due_date', 'worked_hours')
	list_filter = ('status', 'due_date')
