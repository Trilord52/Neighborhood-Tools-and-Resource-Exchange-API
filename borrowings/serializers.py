from rest_framework import serializers

from .models import BorrowRequest


class BorrowRequestSerializer(serializers.ModelSerializer):
    resource = serializers.PrimaryKeyRelatedField(read_only=True)
    requester = serializers.ReadOnlyField(source="requester.username")

    class Meta:
        model = BorrowRequest
        fields = ["id", "resource", "requester", "status", "created_at"]
        read_only_fields = ["id", "resource", "requester", "status", "created_at"]

