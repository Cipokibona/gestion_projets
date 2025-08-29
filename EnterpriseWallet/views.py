from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import EnterpriseWallet
from .serializers import EnterpriseWalletSerializer


class EnterpriseWalletViewSet(viewsets.ModelViewSet):
    queryset = EnterpriseWallet.objects.all()
    serializer_class = EnterpriseWalletSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        enterprise = serializer.validated_data.get('enterprise')
        # Limiter à un seul EnterpriseWallet par entreprise
        if EnterpriseWallet.objects.filter(enterprise=enterprise).exists():
            raise PermissionError("Un EnterpriseWallet existe déjà pour cette entreprise.")
        if hasattr(user, 'role') and user.role in ['manager', 'accountant']:
            serializer.save(user=user)
        else:
            raise PermissionError("Seul le manager ou le caissier peut créer un EnterpriseWallet.")

    def perform_update(self, serializer):
        user = self.request.user
        wallet = self.get_object()

        if wallet.user == user:
            serializer.save()
        else:
            raise PermissionError("Vous ne pouvez mettre à jour que votre propre EnterpriseWallet.")

    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        wallet = self.get_object()

        if wallet.user == user:
            return super().destroy(request, *args, **kwargs)
        else:
            return Response({'detail': "Vous ne pouvez supprimer que votre propre EnterpriseWallet."}, status=status.HTTP_403_FORBIDDEN)
