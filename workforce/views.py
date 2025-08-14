from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import WorkforceGroup
from .serializers import WorkforceGroupSerializer


class WorkforceGroupViewSet(viewsets.ModelViewSet):
    serializer_class = WorkforceGroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WorkforceGroup.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        if hasattr(user, 'role') and user.role == 'manager':
            serializer.save()
        else:
            raise PermissionError("Seul le manager peut créer un groupe de main-d'œuvre.")

    def perform_update(self, serializer):
        user = self.request.user
        if hasattr(user, 'role') and user.role == 'manager':
            workforce_group = self.get_object()
            if workforce_group.project.user == user:
                serializer.save()
            else:
                raise PermissionError("Vous ne pouvez mettre à jour que vos propres groupes.")
        else:
            raise PermissionError("Seul le manager peut mettre à jour un groupe.")

    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        workforce_group = self.get_object()
        if hasattr(user, 'role') and user.role == 'manager' and workforce_group.project.user == user:
            return super().destroy(request, *args, **kwargs)
        else:
            return Response({'detail': "Seul le manager peut supprimer son groupe."}, status=status.HTTP_403_FORBIDDEN)
