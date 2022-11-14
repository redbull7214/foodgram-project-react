from rest_framework import permissions


class AdminOrReadOnly(permissions.BasePermission):
    message = 'You must have admin rights to perform this action.'

    def has_permission(self, request, view):
        return ((request.method in permissions.SAFE_METHODS)
                or (request.user.is_authenticated
                    and request.user.access_administrator
                    ))


class AuthorOrModeratorOrAdmin(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return ((request.method in permissions.SAFE_METHODS)
                or obj.author == request.user
                or (request.user.is_authenticated
                    and request.user.access_administrator)
                or (request.user.is_authenticated
                    and request.user.access_moderator))