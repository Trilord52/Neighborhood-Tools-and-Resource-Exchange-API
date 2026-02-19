from django.conf import settings
from django.db import models

from resources.models import Resource


class BorrowRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        RETURNED = "RETURNED", "Returned"

    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name="borrow_requests",
    )
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="borrow_requests",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["resource"],
                condition=models.Q(status="APPROVED"),
                name="unique_approved_request_per_resource",
            )
        ]

    def __str__(self) -> str:
        return f"{self.requester} -> {self.resource} ({self.status})"

