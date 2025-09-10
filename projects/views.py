from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .models import Project
from .serializers import ProjectSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Project.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        if hasattr(user, 'role') and user.role == 'manager':
            serializer.save(user=user)
        else:
            raise PermissionDenied("Seul le manager peut créer un projet.")

    def perform_update(self, serializer):
        user = self.request.user
        if hasattr(user, 'role') and user.role == 'manager':
            project = self.get_object()
            if project.user == user:
                serializer.save()
            else:
                raise PermissionDenied("Vous ne pouvez mettre à jour que vos propres projets.")
        else:
            raise PermissionDenied("Seul le manager peut mettre à jour un projet.")

    def destroy(self, request, *args, **kwargs):
        user = request.user
        project = self.get_object()

        if hasattr(user, 'role') and user.role == 'manager':
            if project.user == user:
                project.status = 'cancelled'
                project.save()
                return Response({'detail': 'Le projet a été annulé.'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Vous ne pouvez annuler que vos propres projets.'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'detail': 'Seul le manager peut annuler un projet.'}, status=status.HTTP_403_FORBIDDEN)
