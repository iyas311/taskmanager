from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomTokenObtainPairView,
    UserTaskListView,
    UserTaskUpdateView,
    TaskReportView,
)

urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('tasks/', UserTaskListView.as_view(), name='user-tasks'),
    path('tasks/<int:pk>/', UserTaskUpdateView.as_view(), name='user-task-update'),
    path('tasks/<int:pk>/report/', TaskReportView.as_view(), name='task-report'),
]
