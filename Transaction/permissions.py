from rest_framework.permissions import BasePermission


class IsManagerOrAccountant(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name__in=['manager', 'accountant']).exists()
