

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class Task(models.Model):
	STATUS_CHOICES = [
		('pending', 'Pending'),
		('in_progress', 'In Progress'),
		('completed', 'Completed'),
	]
	title = models.CharField(max_length=255)
	description = models.TextField()
	assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tasks')
	assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_tasks')
	due_date = models.DateField()
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
	completion_report = models.TextField(blank=True, null=True)
	worked_hours = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def clean(self):
		"""Model-level validation to ensure data integrity regardless of entry point (API, admin panel, custom views)."""
		# Enforce report and hours when marking as completed
		if self.status == 'completed':
			if not self.completion_report or (isinstance(self.completion_report, str) and not self.completion_report.strip()):
				raise ValidationError({'completion_report': 'This field is required when completing a task.'})
			if self.worked_hours in (None, ''):
				raise ValidationError({'worked_hours': 'This field is required when completing a task.'})
			# Worked hours must be positive
			try:
				if float(self.worked_hours) <= 0:
					raise ValidationError({'worked_hours': 'Worked hours must be a positive number.'})
			except (TypeError, ValueError):
				raise ValidationError({'worked_hours': 'Worked hours must be a valid number.'})

	def save(self, *args, **kwargs):
		# Ensure validation runs on every save (covers custom admin panel forms)
		self.full_clean()
		return super().save(*args, **kwargs)

	def __str__(self):
		return f"{self.title} ({self.get_status_display()})"
