from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import MaterialExpense, MiscExpense
from .serializers import MaterialExpenseSerializer, MiscExpenseSerializer


class MaterialExpenseViewSet(viewsets.ModelViewSet):
    queryset = MaterialExpense.objects.all()
    serializer_class = MaterialExpenseSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if hasattr(user, 'role') and user.role == 'manager':
            serializer.save(user=user)
        else:
            raise PermissionError("Seul le manager peut créer une dépense de matériel.")

    def perform_update(self, serializer):
        user = self.request.user
        expense = self.get_object()
        if hasattr(user, 'role') and user.role == 'manager' and expense.user == user:
            serializer.save()
        else:
            raise PermissionError("Vous ne pouvez mettre à jour que vos propres dépenses.")

    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        expense = self.get_object()
        if hasattr(user, 'role') and user.role == 'manager' and expense.user == user:
            return super().destroy(request, *args, **kwargs)
        else:
            return Response({'detail': "Vous ne pouvez supprimer que vos propres dépenses."}, status=status.HTTP_403_FORBIDDEN)


class MiscExpenseViewSet(viewsets.ModelViewSet):
    queryset = MiscExpense.objects.all()
    serializer_class = MiscExpenseSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if hasattr(user, 'role') and user.role == 'manager':
            serializer.save(user=user)
        else:
            raise PermissionError("Seul le manager peut créer une dépense diverse.")

    def perform_update(self, serializer):
        user = self.request.user
        expense = self.get_object()
        if hasattr(user, 'role') and user.role == 'manager' and expense.user == user:
            serializer.save()
        else:
            raise PermissionError("Vous ne pouvez mettre à jour que vos propres dépenses.")

    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        expense = self.get_object()
        if hasattr(user, 'role') and user.role == 'manager' and expense.user == user:
            return super().destroy(request, *args, **kwargs)
        else:
            return Response({'detail': "Vous ne pouvez supprimer que vos propres dépenses."}, status=status.HTTP_403_FORBIDDEN)
