from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from .models import Advance, MainWallet, TaskWallet
from .serializers import AdvanceSerializer, MainWalletSerializer, TaskWalletSerializer


class AdvanceViewSet(viewsets.ModelViewSet):
    queryset = Advance.objects.all()
    serializer_class = AdvanceSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if hasattr(user, 'role') and user.role == 'manager':
            serializer.save()
        else:
            raise PermissionError("Seul le manager peut créer une avance.")

    def perform_update(self, serializer):
        user = self.request.user
        advance = self.get_object()
        if hasattr(user, 'role') and user.role == 'manager' and advance.project.user == user:
            serializer.save()
        else:
            raise PermissionError("Vous ne pouvez mettre à jour que vos propres avances.")

    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        advance = self.get_object()
        if hasattr(user, 'role') and user.role == 'manager' and advance.project.user == user:
            return super().destroy(request, *args, **kwargs)
        else:
            return Response({'detail': "Vous ne pouvez supprimer que vos propres avances."}, status=status.HTTP_403_FORBIDDEN)


class MainWalletViewSet(viewsets.ModelViewSet):
    queryset = MainWallet.objects.all()
    serializer_class = MainWalletSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        project = serializer.validated_data.get('project')

        if MainWallet.objects.filter(project=project).exists():
            raise PermissionError("Un MainWallet existe déjà pour ce projet.")

        if hasattr(user, 'role') and user.role in ['manager', 'accountant']:
            serializer.save()
        else:
            raise PermissionError("Seul le manager ou le caissier peut créer un MainWallet.")

    def perform_update(self, serializer):
        user = self.request.user
        wallet = self.get_object()

        if hasattr(user, 'role') and user.role in ['manager', 'accountant'] and wallet.project.user == user:
            serializer.save()
        else:
            raise PermissionError("Vous ne pouvez mettre à jour que vos propres MainWallets.")

    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        wallet = self.get_object()

        if hasattr(user, 'role') and user.role in ['manager', 'accountant'] and wallet.project.user == user:
            return super().destroy(request, *args, **kwargs)
        else:
            return Response({'detail': "Vous ne pouvez supprimer que vos propres MainWallets."}, status=status.HTTP_403_FORBIDDEN)


class TaskWalletViewSet(viewsets.ModelViewSet):
    queryset = TaskWallet.objects.all()
    serializer_class = TaskWalletSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user

        if hasattr(user, 'role') and user.role in ['manager', 'accountant']:
            serializer.save(user=user)
        else:
            raise PermissionError("Seul le manager ou le caissier peut créer un TaskWallet.")

    def perform_update(self, serializer):
        user = self.request.user
        taskwallet = self.get_object()

        if hasattr(user, 'role') and user.role in ['manager', 'accountant'] and taskwallet.user == user:
            serializer.save()
        else:
            raise PermissionError("Vous ne pouvez mettre à jour que vos propres TaskWallets.")

    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        taskwallet = self.get_object()

        if hasattr(user, 'role') and user.role in ['manager', 'accountant'] and taskwallet.user == user:
            return super().destroy(request, *args, **kwargs)
        else:
            return Response({'detail': "Vous ne pouvez supprimer que vos propres TaskWallets."}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        taskwallet = self.get_object()

        if not taskwallet.is_closed:
            taskwallet.close()
            return Response({'detail': 'TaskWallet clôturé, le reste est retourné dans le MainWallet.'})
        return Response({'detail': 'Déjà clôturé.'}, status=status.HTTP_400_BAD_REQUEST)
