from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsResourceOwnerOrReadOnly(BasePermission):
    """
    Allow read-only access to any authenticated user.
    Write operations are restricted to the resource owner.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return getattr(obj, "owner", None) == request.user


class IsBorrowRequestResourceOwner(BasePermission):
    """
    Restrict actions on BorrowRequest objects to the owner of the underlying resource.
    """

    def has_object_permission(self, request, view, obj):
        resource = getattr(obj, "resource", None)
        owner = getattr(resource, "owner", None) if resource is not None else None
        return owner == request.user


class IsCommentAuthorOrReadOnly(BasePermission):
    """Allow read for authenticated users; only comment author can update/delete."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return getattr(obj, "author", None) == request.user

