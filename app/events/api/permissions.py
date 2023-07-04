from rest_framework import permissions


class EventPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ["list", "retrieve", "list_talks"]:
            return True
        else:
            return request.user.is_authenticated

    def has_object_permission(self, request, view, event):
        if view.action == "create_talk":
            return event.organizer == request.user
        elif view.action == "list_talks":
            if request.query_params.get("include_all") == "true":
                return event.organizer == request.user
            else:
                return event.is_published or event.organizer == request.user
        elif view.action == "retrieve":
            return event.is_published or event.organizer == request.user
        elif view.action in ["update", "partial_update"]:
            return event.organizer == request.user and not (
                event.has_finished()
            )
        elif view.action == "create_booking":
            return event.organizer != request.user
        elif view.action == "destroy_booking":
            return True
        elif view.action in ["destroy", "publish"]:
            return event.organizer == request.user
        else:
            return False
