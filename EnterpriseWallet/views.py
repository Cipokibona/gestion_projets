from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied

from .models import EnterpriseWallet
from .serializers import EnterpriseWalletSerializer


class EnterpriseWalletViewSet(viewsets.ModelViewSet):
    queryset = EnterpriseWallet.objects.all()
    serializer_class = EnterpriseWalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if request.user.role not in ['manager', 'accountant']:
            raise PermissionDenied("Seul un utilisateur avec le rôle 'manager' ou 'accountant' peut créer un wallet.")

        if EnterpriseWallet.objects.filter(user=request.user).exists():
            return Response(
                {"detail": "Un wallet existe déjà pour cette entreprise."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        wallet = self.get_object()
        if wallet.user != request.user:
            raise PermissionDenied("Seul le créateur du wallet peut le modifier.")
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        wallet = self.get_object()
        if wallet.user != request.user:
            raise PermissionDenied("Seul le créateur du wallet peut le modifier.")
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        wallet = self.get_object()
        if wallet.user != request.user:
            raise PermissionDenied("Seul le créateur du wallet peut le supprimer.")
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['get'], url_path='balance')
    def get_balance(self, request, pk=None):
        wallet = self.get_object()

        # # Vérifie si l'utilisateur a le droit de voir ce wallet
        # if wallet.user != request.user:
        #     raise PermissionDenied("Vous n'avez pas accès à ce wallet.")

        return Response(
            {"wallet_id": wallet.id, "wallet_name": wallet.name, "balance": wallet.total_balance()},
            status=status.HTTP_200_OK
        )
