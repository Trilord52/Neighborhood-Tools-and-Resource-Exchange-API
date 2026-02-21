from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from neighborhood_exchange.permissions import IsCommentAuthorOrReadOnly, IsResourceOwnerOrReadOnly

from .models import Category, Comment, Resource, ResourceLike
from .serializers import CategorySerializer, CommentSerializer, ResourceSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class ResourceViewSet(viewsets.ModelViewSet):
    serializer_class = ResourceSerializer
    permission_classes = [permissions.IsAuthenticated, IsResourceOwnerOrReadOnly]

    filterset_fields = ["is_available", "category"]
    search_fields = ["name", "description"]
    ordering_fields = ["created_at", "name"]

    def get_queryset(self):
        return (
            Resource.objects.select_related("owner", "category")
            .all()
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"], url_path="like")
    def like(self, request, pk=None):
        resource = self.get_object()
        _, created = ResourceLike.objects.get_or_create(
            resource=resource,
            user=request.user,
        )
        return Response(
            {"detail": "Liked." if created else "Already liked."},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="unlike")
    def unlike(self, request, pk=None):
        resource = self.get_object()
        deleted, _ = ResourceLike.objects.filter(
            resource=resource,
            user=request.user,
        ).delete()
        return Response(
            {"detail": "Unliked." if deleted else "Not liked."},
            status=status.HTTP_200_OK,
        )


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsCommentAuthorOrReadOnly]

    def get_queryset(self):
        resource_pk = self.kwargs.get("resource_pk")
        return (
            Comment.objects.filter(resource_id=resource_pk)
            .select_related("author", "resource")
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            resource_id=self.kwargs["resource_pk"],
        )


