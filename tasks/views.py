
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Task
from .serializers import TaskSerializer, TaskReportSerializer
from accounts.models import User
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
	@classmethod
	def get_token(cls, user):
		token = super().get_token(user)
		token['role'] = user.role
		return token
class CustomTokenObtainPairView(TokenObtainPairView):
	serializer_class = CustomTokenObtainPairSerializer

class UserTaskListView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'role', None) == 'superadmin':
            return Task.objects.all()
        if getattr(user, 'role', None) == 'admin':
            return Task.objects.filter(assigned_to__assigned_admin=user)
        return Task.objects.filter(assigned_to=user)

class UserTaskUpdateView(generics.UpdateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(assigned_to=self.request.user)

    http_method_names = ['put']

class TaskReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        user = request.user
        task = get_object_or_404(Task, pk=pk)
        if task.status != 'completed':
            return Response({'error': 'Task is not completed.'}, status=status.HTTP_400_BAD_REQUEST)
        if user.role not in ['admin', 'superadmin']:
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        if user.role == 'admin':
            manages_user = getattr(task.assigned_to, 'assigned_admin_id', None) == user.id
            assigned_by_admin = getattr(task, 'assigned_by_id', None) == user.id
            if not (manages_user or assigned_by_admin):
                return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = TaskReportSerializer(task)
        return Response(serializer.data)
