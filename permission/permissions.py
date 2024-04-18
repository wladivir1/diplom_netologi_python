from rest_framework import permissions


class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user == obj.user and request.user.is_active or request.user.is_staff
