from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Account
from .serializers import AccountSerializer


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if hasattr(user, 'role') and user.role in ['manager', 'accountant']:
            serializer.save()
        else:
            raise PermissionError("Seul le manager ou le caissier peut créer un compte.")

    def perform_update(self, serializer):
        user = self.request.user
        account = self.get_object()
        if hasattr(user, 'role') and user.role in ['manager', 'accountant'] and account.project.user == user:
            serializer.save()
        else:
            raise PermissionError("Vous ne pouvez mettre à jour que vos propres comptes.")

    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        account = self.get_object()
        if hasattr(user, 'role') and user.role in ['manager', 'accountant'] and account.project.user == user:
            return super().destroy(request, *args, **kwargs)
        else:
            return Response({'detail': "Vous ne pouvez supprimer que vos propres comptes."}, status=status.HTTP_403_FORBIDDEN)
