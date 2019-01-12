from rest_framework import permissions


class IsContactsOwner(permissions.BasePermission):

    def has_permission(self, request, view):
        return view.kwargs['pk'] == request.user.pk
