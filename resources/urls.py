from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, CommentViewSet, ResourceViewSet

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"resources", ResourceViewSet, basename="resource")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "resources/<int:resource_pk>/comments/",
        CommentViewSet.as_view({"get": "list", "post": "create"}),
        name="resource-comments-list",
    ),
    path(
        "resources/<int:resource_pk>/comments/<int:pk>/",
        CommentViewSet.as_view(
            {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
        ),
        name="resource-comment-detail",
    ),
]

