from rest_framework import serializers
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
        return Transaction.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        user = self.request.user
        if hasattr(user, 'role') and user.role in ['manager', 'accountant']:
            serializer.save(user=user)
        else:
            raise serializers.ValidationError("Seul le manager ou le caissier peut créer une transaction.")

    def perform_update(self, serializer):
        transaction = self.get_object()
        user = self.request.user
        if transaction.user != user:
            raise serializers.ValidationError("Vous ne pouvez modifier que vos propres transactions.")
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        transaction = self.get_object()
        user = request.user
        if transaction.user != user:
            return Response({'detail': "Vous ne pouvez supprimer que vos propres transactions."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_transaction(self, request, pk=None):
        transaction = self.get_object()
        user = request.user
        if transaction.user != user:
            return Response({'detail': "Vous ne pouvez annuler que vos propres transactions."}, status=status.HTTP_403_FORBIDDEN)
        if transaction.is_cancelled:
            return Response({'detail': 'Transaction déjà annulée.'}, status=status.HTTP_400_BAD_REQUEST)
        reason = request.data.get('reason', 'Annulation sans motif précisé')
        transaction.cancel(reason=reason, cancelled_by=user)
        Advance.objects.filter(account=transaction.account).update(is_valid=False)
        GeneralExpense.objects.filter(account=transaction.account).update(is_valid=False)
        return Response({'detail': 'Transaction annulée avec succès.'}, status=status.HTTP_200_OK)


class TransactionErrorLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TransactionErrorLog.objects.all()
    serializer_class = TransactionErrorLogSerializer
    permission_classes = [IsAuthenticated, IsManagerOrAccountant]


# class TransactionViewSet(viewsets.ModelViewSet):
#     serializer_class = TransactionSerializer
#     permission_classes = [IsAuthenticated, IsManagerOrAccountant]

#     def get_queryset(self):
#         return Transaction.objects.filter(user=self.request.user)

#     def perform_create(self, serializer):
#         user = self.request.user
#         if hasattr(user, 'role') and user.role in ['manager', 'accountant']:
#             serializer.save(user=user)
#             # try:
#             #     serializer.save(user=user)
#             # except serializers.ValidationError as e:
#             #     # Log automatique des erreurs
#             #     TransactionErrorLog.objects.create(
#             #         user=user,
#             #         transaction_type=serializer.validated_data.get('transaction_type'),
#             #         account=serializer.validated_data.get('account', None),
#             #         destination_account=serializer.validated_data.get('destination_account', None),
#             #         amount=serializer.validated_data.get('amount', None),
#             #         error_message=str(e)
#             #     )
#             #     raise e
#         else:
#             raise serializers.ValidationError("Seul le manager ou le caissier peut créer une transaction.")

#     def perform_update(self, serializer):
#         transaction = self.get_object()
#         user = self.request.user

#         if transaction.user != user:
#             raise PermissionError("Vous ne pouvez modifier que vos propres transactions.")

#         serializer.save()

#     def destroy(self, request, *args, **kwargs):
#         transaction = self.get_object()
#         user = request.user

#         if transaction.user != user:
#             return Response({'detail': "Vous ne pouvez supprimer que vos propres transactions."}, status=status.HTTP_403_FORBIDDEN)

#         return super().destroy(request, *args, **kwargs)

#     @action(detail=True, methods=['post'], url_path='cancel')
#     def cancel_transaction(self, request, pk=None):
#         transaction = self.get_object()
#         user = request.user

#         if transaction.user != user:
#             return Response({'detail': "Vous ne pouvez annuler que vos propres transactions."}, status=status.HTTP_403_FORBIDDEN)

#         if transaction.is_cancelled:
#             return Response({'detail': 'Transaction déjà annulée.'}, status=status.HTTP_400_BAD_REQUEST)

#         reason = request.data.get('reason', 'Annulation sans motif précisé')
#         transaction.cancel(reason=reason, cancelled_by=user)

#         Advance.objects.filter(account=transaction.account).update(is_valid=False)
#         GeneralExpense.objects.filter(account=transaction.account).update(is_valid=False)

#         return Response({'detail': 'Transaction annulée avec succès.'}, status=status.HTTP_200_OK)


# # class TransactionViewSet(viewsets.ModelViewSet):
# #     serializer_class = TransactionSerializer
# #     permission_classes = [IsAuthenticated, IsManagerOrAccountant]

# #     def get_queryset(self):
# #         return Transaction.objects.filter(user=self.request.user)

# #     def perform_create(self, serializer):
# #         user = self.request.user
# #         if hasattr(user, 'role') and user.role in ['manager', 'accountant']:
# #             serializer.save()
# #             # serializer.save(user=user)
# #         else:
# #             raise PermissionError("Seul le manager ou le caissier peut créer une transaction.")

# #     def perform_update(self, serializer):
# #         transaction = self.get_object()
# #         user = self.request.user

# #         if transaction.user != user:
# #             raise PermissionError("Vous ne pouvez modifier que vos propres transactions.")

# #         serializer.save()

# #     def destroy(self, request, *args, **kwargs):
# #         transaction = self.get_object()
# #         user = request.user

# #         if transaction.user != user:
# #             return Response({'detail': "Vous ne pouvez supprimer que vos propres transactions."}, status=status.HTTP_403_FORBIDDEN)

# #         return super().destroy(request, *args, **kwargs)

# #     @action(detail=True, methods=['post'], url_path='cancel')
# #     def cancel_transaction(self, request, pk=None):
# #         transaction = self.get_object()
# #         user = request.user

# #         if transaction.user != user:
# #             return Response({'detail': "Vous ne pouvez annuler que vos propres transactions."}, status=status.HTTP_403_FORBIDDEN)

# #         if transaction.is_cancelled:
# #             return Response({'detail': 'Transaction déjà annulée.'}, status=status.HTTP_400_BAD_REQUEST)

# #         reason = request.data.get('reason', 'Annulation sans motif précisé')
# #         transaction.cancel(reason=reason, cancelled_by=user)

# #         Advance.objects.filter(account=transaction.account).update(is_valid=False)
# #         GeneralExpense.objects.filter(account=transaction.account).update(is_valid=False)

# #         return Response({'detail': 'Transaction annulée avec succès.'}, status=status.HTTP_200_OK)


# class TransactionErrorLogViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = TransactionErrorLog.objects.all()
#     serializer_class = TransactionErrorLogSerializer
#     permission_classes = [IsAuthenticated, IsManagerOrAccountant]
