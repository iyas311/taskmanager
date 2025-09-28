
from django.contrib.auth.views import LoginView

class RoleBasedLoginView(LoginView):
	def get_success_url(self):
		user = self.request.user
		if hasattr(user, 'role'):
			if user.role == 'superadmin':
				return '/adminpanel/superadmin/'
			elif user.role == 'admin':
				return '/adminpanel/admin/'
			else:
				return '/adminpanel/'
		return super().get_success_url()
