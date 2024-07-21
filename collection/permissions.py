from rest_framework import permissions


class IsCashCollector(permissions.BasePermission):
    """
    Custom permission to allow only CashCollector users.
    """

    def has_permission(self, request, view):
        return request.user and hasattr(request.user, "cash_collector")


class IsManager(permissions.BasePermission):
    """
    Custom permission to allow only Manager users.
    """

    def has_permission(self, request, view):
        return request.user and hasattr(request.user, "manager")


class IsManagerOrCollector(permissions.BasePermission):
    """
    Custom permission to allow only Manager users.
    """

    def has_permission(self, request, view):
        return request.user and (
            hasattr(request.user, "manager")
            or hasattr(request.user, "cash_collector")
            or request.user.is_superuser
        )
