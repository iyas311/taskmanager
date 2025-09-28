

from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
	ROLE_CHOICES = [
		('user', 'User'),
		('admin', 'Admin'),
		('superadmin', 'SuperAdmin'),
	]
	role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
	assigned_admin = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, limit_choices_to={'role': 'admin'}, related_name='assigned_users')

	def __str__(self):
		return f"{self.username} ({self.get_role_display()})"
