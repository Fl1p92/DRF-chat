from rest_framework import permissions


class IsOwner(permissions.BasePermission):

    def has_permission(self, request, view):
        return str(view.kwargs.get('pk')) == str(request.user.pk)
