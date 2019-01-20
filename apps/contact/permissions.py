from rest_framework import permissions


class IsOwner(permissions.BasePermission):

    def has_permission(self, request, view):
        return view.kwargs.get('pk') == request.user.pk


class IsContactOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.contacts_list.owner == request.user
