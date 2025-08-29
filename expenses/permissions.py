from rest_framework.permissions import BasePermission


class ProjectExpenseAllowed(BasePermission):
    """
    Autorise la création/modification de dépenses seulement si le projet est dans un statut autorisé.
    """
    allowed_status = ['in_progress']

    def has_object_permission(self, request, view, obj):
        # obj doit avoir un champ 'project'
        return getattr(obj.project, 'status', None) in self.allowed_status

    def has_permission(self, request, view):
        # Pour la création, on vérifie dans perform_create
        return True
