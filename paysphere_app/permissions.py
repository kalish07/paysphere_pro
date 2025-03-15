from rest_framework import permissions

class IsHRAdmin(permissions.BasePermission):
    """Allow only HR/Admin to perform certain actions."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.group == 'HR'

class IsEmployeeOrReadOnly(permissions.BasePermission):
    """Allow employees to view their own details but not modify others."""
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and (request.user == obj or request.user.group == 'HR')