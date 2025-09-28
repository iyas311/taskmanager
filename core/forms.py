
from django import forms
from accounts.models import User
from tasks.models import Task

class AssignUserToAdminForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.filter(role='user'))
    admin = forms.ModelChoiceField(queryset=User.objects.filter(role='admin'))

class UserEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit assigned_admin choices to users with admin role
        if 'assigned_admin' in self.fields:
            self.fields['assigned_admin'].queryset = User.objects.filter(role='admin')

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'assigned_admin', 'is_active']
        help_texts = {
            'username': '',  # remove default "150 characters or fewer..." help text
        }

class TaskEditForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'status', 'completion_report', 'worked_hours', 'assigned_to']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

class TaskCreateForm(forms.ModelForm):
    class Meta:
        model = Task
        # Exclude completion_report and worked_hours on creation
        fields = ['title', 'description', 'due_date', 'status', 'assigned_to']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }
