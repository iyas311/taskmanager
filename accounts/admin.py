from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
	fieldsets = DjangoUserAdmin.fieldsets + (
		('Role', {'fields': ('role',)}),
	)
	list_display = ('username', 'email', 'role', 'is_staff', 'is_superuser')
	list_filter = ('role', 'is_staff', 'is_superuser')
