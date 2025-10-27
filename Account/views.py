from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .models import Account
from .serializers import AccountSerializer


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if request.user.role not in ['manager', 'accountant']:
            raise PermissionDenied("Seul un utilisateur avec le rôle 'manager' ou 'accountant' peut créer un compte.")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        account = self.get_object()
        if account.user != request.user:
            raise PermissionDenied("Seul le créateur du compte peut le modifier.")
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        account = self.get_object()
        if account.user != request.user:
            raise PermissionDenied("Seul le créateur du compte peut le modifier.")
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        account = self.get_object()
        if account.user != request.user:
            raise PermissionDenied("Seul le créateur du compte peut le supprimer.")
        if account.balance != 0:
            return Response(
                {"detail": "Impossible de supprimer un compte avec un solde non nul."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)
