from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .models import Transaction, TransactionErrorLog
from .serializers import TransactionSerializer, TransactionErrorLogSerializer
from .permissions import IsManagerOrAccountant

from finance.models import Advance
from expenses.models import GeneralExpense


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, IsManagerOrAccountant]

    def get_queryset(self):
        return Transaction.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_transaction(self, request, pk=None):
        transaction = self.get_object()
        if transaction.is_cancelled:
            return Response({'detail': 'Transaction déjà annulée.'}, status=status.HTTP_400_BAD_REQUEST)
        reason = request.data.get('reason', 'Annulation sans motif précisé')
        transaction.cancel(reason=reason, cancelled_by=request.user)
        Advance.objects.filter(account=transaction.account).update(is_valid=False)
        GeneralExpense.objects.filter(account=transaction.account).update(is_valid=False)
        return Response({'detail': 'Transaction annulée avec succès.'}, status=status.HTTP_200_OK)


class TransactionErrorLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TransactionErrorLog.objects.all()
    serializer_class = TransactionErrorLogSerializer
    permission_classes = [IsAuthenticated, IsManagerOrAccountant]
