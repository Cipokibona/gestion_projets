from rest_framework.permissions import BasePermission


class IsManagerOrAccountant(BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, 'role', None) in ['manager', 'accountant']
