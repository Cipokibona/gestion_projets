from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import MaterialExpense, MiscExpense, GeneralExpense, CompanyExpense
from .serializers import MaterialExpenseSerializer, MiscExpenseSerializer, GeneralExpenseSerializer, CompanyExpenseSerializer
from .permissions import ProjectExpenseAllowed


class MaterialExpenseViewSet(viewsets.ModelViewSet):
    queryset = MaterialExpense.objects.all()
    serializer_class = MaterialExpenseSerializer
    permission_classes = [IsAuthenticated, ProjectExpenseAllowed]

    def perform_create(self, serializer):
        user = self.request.user
        project = serializer.validated_data.get('project')

        if project.status not in ProjectExpenseAllowed.allowed_status:
            raise PermissionError("Vous ne pouvez pas ajouter de dépense à un projet qui n'est pas en cours.")

        if hasattr(user, 'role') and user.role == 'manager':
            serializer.save(user=user)
        else:
            raise PermissionError("Seul le manager peut créer une dépense de matériel.")

    def perform_update(self, serializer):
        user = self.request.user
        expense = self.get_object()

        if expense.project.status not in ProjectExpenseAllowed.allowed_status:
            raise PermissionError("Vous ne pouvez pas modifier une dépense d'un projet qui n'est pas en cours.")

        if hasattr(user, 'role') and user.role == 'manager' and expense.user == user:
            serializer.save()
        else:
            raise PermissionError("Vous ne pouvez mettre à jour que vos propres dépenses.")

    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        expense = self.get_object()

        if expense.project.status not in ProjectExpenseAllowed.allowed_status:
            raise PermissionError("Vous ne pouvez pas supprimer une dépense d'un projet qui n'est pas en cours.")

        if hasattr(user, 'role') and user.role == 'manager' and expense.user == user:
            return super().destroy(request, *args, **kwargs)
        else:
            return Response({'detail': "Vous ne pouvez supprimer que vos propres dépenses."}, status=status.HTTP_403_FORBIDDEN)


class MiscExpenseViewSet(viewsets.ModelViewSet):
    queryset = MiscExpense.objects.all()
    serializer_class = MiscExpenseSerializer
    permission_classes = [IsAuthenticated, ProjectExpenseAllowed]

    def perform_create(self, serializer):
        user = self.request.user
        project = serializer.validated_data.get('project')

        if project.status not in ProjectExpenseAllowed.allowed_status:
            raise PermissionError("Vous ne pouvez pas ajouter de dépense à un projet qui n'est pas en cours.")

        if hasattr(user, 'role') and user.role == 'manager':
            serializer.save(user=user)
        else:
            raise PermissionError("Seul le manager peut créer une dépense diverse.")

    def perform_update(self, serializer):
        user = self.request.user
        expense = self.get_object()

        if expense.project.status not in ProjectExpenseAllowed.allowed_status:
            raise PermissionError("Vous ne pouvez pas modifier une dépense d'un projet qui n'est pas en cours.")

        if hasattr(user, 'role') and user.role == 'manager' and expense.user == user:
            serializer.save()
        else:
            raise PermissionError("Vous ne pouvez mettre à jour que vos propres dépenses.")

    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        expense = self.get_object()

        if expense.project.status not in ProjectExpenseAllowed.allowed_status:
            raise PermissionError("Vous ne pouvez pas supprimer une dépense d'un projet qui n'est pas en cours.")

        if hasattr(user, 'role') and user.role == 'manager' and expense.user == user:
            return super().destroy(request, *args, **kwargs)
        else:
            return Response({'detail': "Vous ne pouvez supprimer que vos propres dépenses."}, status=status.HTTP_403_FORBIDDEN)


class GeneralExpenseViewSet(viewsets.ModelViewSet):
    queryset = GeneralExpense.objects.all()
    serializer_class = GeneralExpenseSerializer
    permission_classes = [IsAuthenticated, ProjectExpenseAllowed]

    def perform_create(self, serializer):
        user = self.request.user
        project = serializer.validated_data.get('project')

        if project.status not in ProjectExpenseAllowed.allowed_status:
            raise PermissionError("Vous ne pouvez pas ajouter de dépense à un projet qui n'est pas en cours.")

        if hasattr(user, 'role') and user.role in ['manager', 'accountant']:
            serializer.save(user=user)
        else:
            raise PermissionError("Seul le manager ou le caissier peut créer une dépense générale.")

    def perform_update(self, serializer):
        user = self.request.user
        expense = self.get_object()

        if expense.project.status not in ProjectExpenseAllowed.allowed_status:
            raise PermissionError("Vous ne pouvez pas modifier une dépense d'un projet qui n'est pas en cours.")

        if hasattr(user, 'role') and user.role in ['manager', 'accountant'] and expense.user == user:
            serializer.save()
        else:
            raise PermissionError("Vous ne pouvez mettre à jour que vos propres dépenses.")

    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        expense = self.get_object()

        if expense.project.status not in ProjectExpenseAllowed.allowed_status:
            raise PermissionError("Vous ne pouvez pas supprimer une dépense d'un projet qui n'est pas en cours.")

        if hasattr(user, 'role') and user.role in ['manager', 'accountant'] and expense.user == user:
            return super().destroy(request, *args, **kwargs)
        else:
            return Response({'detail': "Vous ne pouvez supprimer que vos propres dépenses."}, status=status.HTTP_403_FORBIDDEN)

class CompanyExpenseViewSet(viewsets.ModelViewSet):
    queryset = CompanyExpense.objects.all().order_by('-created_at')
    serializer_class = CompanyExpenseSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user

        if hasattr(user, 'role') and user.role in ['manager', 'accountant']:
            serializer.save(user=user)
        else:
            raise PermissionError("Seul le manager ou le caissier peut créer une dépense de l'entreprise.")

    def perform_update(self, serializer):
        user = self.request.user
        expense = self.get_object()

        if hasattr(user, 'role') and user.role in ['manager', 'accountant'] and expense.user == user:
            serializer.save()
        else:
            raise PermissionError("Vous ne pouvez mettre à jour que vos propres dépenses.")

    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        expense = self.get_object()

        if hasattr(user, 'role') and user.role in ['manager', 'accountant'] and expense.user == user:
            return super().destroy(request, *args, **kwargs)
        else:
            return Response({'detail': "Vous ne pouvez supprimer que vos propres dépenses."}, status=status.HTTP_403_FORBIDDEN)