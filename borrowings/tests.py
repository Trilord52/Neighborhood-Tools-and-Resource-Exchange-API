from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from resources.models import Category, Resource
from .models import BorrowRequest


User = get_user_model()


class BorrowRequestTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner", email="owner@example.com", password="password123"
        )
        self.requester = User.objects.create_user(
            username="requester", email="requester@example.com", password="password123"
        )
        category = Category.objects.create(name="Books")
        self.resource = Resource.objects.create(
            owner=self.owner,
            name="Book",
            description="A book",
            category=category,
        )

    def test_create_and_approve_borrow_request(self):
        self.client.force_authenticate(self.requester)
        url = reverse("borrow-request-list")
        response = self.client.post(
            url, {"resource_id": self.resource.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        borrow_request_id = response.data["id"]
        self.resource.refresh_from_db()
        self.assertTrue(self.resource.is_available)

        self.client.force_authenticate(self.owner)
        approve_url = reverse("borrow-request-approve", args=[borrow_request_id])
        approve_response = self.client.put(approve_url, {}, format="json")
        self.assertEqual(approve_response.status_code, status.HTTP_200_OK)
        self.resource.refresh_from_db()
        self.assertFalse(self.resource.is_available)
        self.assertEqual(
            BorrowRequest.objects.get(id=borrow_request_id).status,
            BorrowRequest.Status.APPROVED,
        )

    def test_cannot_request_own_resource(self):
        self.client.force_authenticate(self.owner)
        url = reverse("borrow-request-list")
        response = self.client.post(
            url, {"resource_id": self.resource.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_only_owner_can_approve(self):
        self.client.force_authenticate(self.requester)
        url = reverse("borrow-request-list")
        response = self.client.post(
            url, {"resource_id": self.resource.id}, format="json"
        )
        borrow_request_id = response.data["id"]

        other_user = User.objects.create_user(
            username="other", email="other@example.com", password="password123"
        )
        self.client.force_authenticate(other_user)
        approve_url = reverse("borrow-request-approve", args=[borrow_request_id])
        approve_response = self.client.put(approve_url, {}, format="json")
        self.assertEqual(approve_response.status_code, status.HTTP_403_FORBIDDEN)
