from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BorrowRequestViewSet

router = DefaultRouter()
router.register(r"borrow-requests", BorrowRequestViewSet, basename="borrow-request")


urlpatterns = [
    path("", include(router.urls)),
]

