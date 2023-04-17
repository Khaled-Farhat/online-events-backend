from rest_framework import permissions


class TalkPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, talk):
        if talk.has_started():
            return False
        elif view.action in ["update", "partial_update"]:
            return request.user == talk.speaker
        elif view.action == "destroy":
            return talk.event.organizer == request.user
        else:
            return False
