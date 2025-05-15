from rest_framework.permissions import BasePermission


class IsStaff(BasePermission):
    """
    Restricts access to staff users only.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff


class IsOwner(BasePermission):
    """
    For objects that are owned by a user. For example, a task instance.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user.id == request.user.id


class IsSelfOrStaff(BasePermission):
    """
    Required when only a staff user and the instance (in this case the user) can
    modify the instance.
    """
    def has_object_permission(self, request, view, obj):
        if obj.id == request.user.id:
            return True
        return request.user.is_staff
