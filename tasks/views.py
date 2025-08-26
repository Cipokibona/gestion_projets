from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model

from .models import Task
from .serializers import TaskSerializer

User = get_user_model()


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Seuls les managers voient toutes les tâches
        if hasattr(user, 'role') and user.role == 'manager':
            return Task.objects.all()
        return Task.objects.none()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        task = self.get_object()
        user = self.request.user
        # Seul le créateur ou le manager assigné peut modifier
        if (hasattr(user, 'role') and user.role == 'manager' and
            (task.created_by == user or task.assigned_to == user)):
            serializer.save()
        else:
            raise PermissionError("Seul le créateur ou le manager assigné peut modifier cette tâche.")

    def destroy(self, request, *args, **kwargs):
        task = self.get_object()
        user = request.user
        if (hasattr(user, 'role') and user.role == 'manager' and
            (task.created_by == user or task.assigned_to == user)):
            return super().destroy(request, *args, **kwargs)
        else:
            return Response({'detail': "Seul le créateur ou le manager assigné peut supprimer cette tâche."}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=True, methods=['post'], url_path='assign')
    def assign(self, request, pk=None):
        task = self.get_object()
        user = request.user
        assigned_id = request.data.get('assigned_to')
        if task.created_by != user:
            return Response({'detail': "Seul le créateur peut assigner la tâche."}, status=status.HTTP_403_FORBIDDEN)
        try:
            assigned_user = User.objects.get(pk=assigned_id)
        except User.DoesNotExist:
            return Response({'detail': "Utilisateur introuvable."}, status=status.HTTP_400_BAD_REQUEST)
        if getattr(assigned_user, 'role', None) != 'manager':
            return Response({'detail': "Vous ne pouvez assigner la tâche qu'à un utilisateur manager."}, status=status.HTTP_400_BAD_REQUEST)
        task.assigned_to = assigned_user
        task.save()
        return Response({'detail': f"Tâche assignée à {assigned_user.username}."})
