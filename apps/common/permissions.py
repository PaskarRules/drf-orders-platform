from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrAdmin(BasePermission):
    """Allow access to object owner or admin users."""

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.user == request.user


class IsAdminOrReadOnly(BasePermission):
    """Allow read access to anyone, write access only to admins."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)
