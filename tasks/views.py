from rest_framework import viewsets, status
from rest_framework.exceptions import PermissionDenied
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
        if hasattr(user, 'role') and user.role == 'manager':
            return Task.objects.all()
        # return Task.objects.none()
        raise PermissionDenied("Seuls les managers ont le droit de voir les tâches.")

    def perform_create(self, serializer):
        user = self.request.user
        project = serializer.validated_data.get('project')
        if not (hasattr(user, 'role') and user.role == 'manager'):
            raise PermissionDenied("Seul le manager peut créer une tâche.")
        if project.status != 'in_progress':
            raise PermissionDenied("Aucune action n'est autorisée sur les tâches d'un projet qui n'est pas en cours.")
        serializer.save(created_by=user)

    def perform_update(self, serializer):
        task = self.get_object()
        user = self.request.user
        if task.project.status != 'in_progress':
            raise PermissionDenied("Aucune action n'est autorisée sur les tâches d'un projet qui n'est pas en cours.")
        if (hasattr(user, 'role') and user.role == 'manager' and
            (task.created_by == user or task.assigned_to == user)):
            serializer.save()
        else:
            raise PermissionDenied("Seul le créateur ou le manager assigné peut modifier cette tâche.")

    def destroy(self, request, *args, **kwargs):
        task = self.get_object()
        user = request.user
        if task.project.status != 'in_progress':
            return Response({'detail': "Aucune action n'est autorisée sur les tâches d'un projet qui n'est pas en cours."}, status=status.HTTP_403_FORBIDDEN)
        if (hasattr(user, 'role') and user.role == 'manager' and
            (task.created_by == user or task.assigned_to == user)):
            return super().destroy(request, *args, **kwargs)
        else:
            return Response({'detail': "Seul le créateur ou le manager assigné peut supprimer cette tâche."}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=True, methods=['post'], url_path='assign')
    def assign(self, request, pk=None):
        task = self.get_object()
        user = request.user
        if task.project.status != 'in_progress':
            return Response({'detail': "Aucune action n'est autorisée sur les tâches d'un projet qui n'est pas en cours."}, status=status.HTTP_403_FORBIDDEN)
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
