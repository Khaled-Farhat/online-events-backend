from rest_framework import permissions


class EventPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ["list", "retrieve"]:
            return True
        else:
            return request.user.is_authenticated

    def has_object_permission(self, request, view, event):
        if view.action == "retrieve":
            return event.is_published or event.organizer == request.user
        elif view.action in ["update", "partial_update"]:
            return event.organizer == request.user and not (
                event.has_finished()
            )
        elif view.action in ["destroy", "publish"]:
            return event.organizer == request.user
        else:
            return False
