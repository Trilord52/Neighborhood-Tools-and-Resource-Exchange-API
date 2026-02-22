from django.shortcuts import get_object_or_404
from django.db import models
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from neighborhood_exchange.permissions import IsBorrowRequestResourceOwner
from resources.models import Resource

from .models import BorrowRequest
from .serializers import BorrowRequestSerializer


class BorrowRequestViewSet(viewsets.ModelViewSet):
    serializer_class = BorrowRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    filterset_fields = ["status"]
    ordering_fields = ["created_at"]

    def get_permissions(self):
        if self.action in ["approve", "reject", "return_item"]:
            return [
                permissions.IsAuthenticated(),
                IsBorrowRequestResourceOwner(),
            ]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        queryset = BorrowRequest.objects.select_related(
            "resource", "requester"
        ).filter(
            models.Q(requester=user) | models.Q(resource__owner=user)
        ).order_by("-created_at")

        role = self.request.query_params.get("role")

        if role == "requester":
            queryset = queryset.filter(requester=user)
        elif role == "owner":
            queryset = queryset.filter(resource__owner=user)

        return queryset

    def create(self, request, *args, **kwargs):
        resource_id = request.data.get("resource_id")
        if not resource_id:
            return Response(
                {"detail": "resource_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        resource = get_object_or_404(Resource, pk=resource_id)

        if resource.owner == request.user:
            return Response(
                {"detail": "You cannot request your own resource."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not resource.is_available:
            return Response(
                {"detail": "This resource is not currently available."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        borrow_request = BorrowRequest.objects.create(
            resource=resource,
            requester=request.user,
        )
        serializer = self.get_serializer(borrow_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["put"], url_path="approve")
    def approve(self, request, pk=None):
        borrow_request = self.get_object()
        if borrow_request.status != BorrowRequest.Status.PENDING:
            return Response(
                {"detail": "Only pending requests can be approved."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Enforced also by database constraint, but we provide a clear error first.
        if BorrowRequest.objects.filter(
            resource=borrow_request.resource,
            status=BorrowRequest.Status.APPROVED,
        ).exclude(pk=borrow_request.pk).exists():
            return Response(
                {"detail": "Another approved request already exists for this resource."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        borrow_request.status = BorrowRequest.Status.APPROVED
        borrow_request.save()

        borrow_request.resource.is_available = False
        borrow_request.resource.save()

        return Response(self.get_serializer(borrow_request).data)

    @action(detail=True, methods=["put"], url_path="reject")
    def reject(self, request, pk=None):
        borrow_request = self.get_object()
        if borrow_request.status != BorrowRequest.Status.PENDING:
            return Response(
                {"detail": "Only pending requests can be rejected."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        borrow_request.status = BorrowRequest.Status.REJECTED
        borrow_request.save()

        return Response(self.get_serializer(borrow_request).data)

    @action(detail=True, methods=["put"], url_path="return")
    def return_item(self, request, pk=None):
        borrow_request = self.get_object()
        if borrow_request.status != BorrowRequest.Status.APPROVED:
            return Response(
                {"detail": "Only approved requests can be marked as returned."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        borrow_request.status = BorrowRequest.Status.RETURNED
        borrow_request.save()

        # If no other approved requests remain, mark resource as available again.
        if not BorrowRequest.objects.filter(
            resource=borrow_request.resource,
            status=BorrowRequest.Status.APPROVED,
        ).exists():
            borrow_request.resource.is_available = True
            borrow_request.resource.save()

        return Response(self.get_serializer(borrow_request).data)

