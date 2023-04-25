from rest_framework import permissions


class UserPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, user):
        if view.action == "retrieve":
            return True
        elif view.action in ["update", "partial_update", "list_talks"]:
            return request.user == user
