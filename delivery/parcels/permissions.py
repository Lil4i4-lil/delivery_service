from rest_framework import permissions


class isOwner(permissions.BasePermission):
    """Permission: только владелец посылки может получить доступ"""

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
