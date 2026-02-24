from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from .models import Category, Resource


User = get_user_model()


class ResourceTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="owner", email="owner@example.com", password="password123"
        )
        self.client.force_authenticate(self.user)

    def test_create_resource(self):
        category = Category.objects.create(name="Tools")
        url = reverse("resource-list")
        data = {
            "name": "Ladder",
            "description": "Tall ladder",
            "category": category.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Resource.objects.count(), 1)
        resource = Resource.objects.get()
        self.assertEqual(resource.owner, self.user)

    def test_non_owner_cannot_update_resource(self):
        category = Category.objects.create(name="Tools")
        resource = Resource.objects.create(
            owner=self.user,
            name="Hammer",
            description="Heavy hammer",
            category=category,
        )
        other_user = User.objects.create_user(
            username="other", email="other@example.com", password="password123"
        )
        self.client.force_authenticate(other_user)
        url = reverse("resource-detail", args=[resource.id])
        response = self.client.patch(url, {"name": "Updated"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_resources_by_availability_and_category(self):
        tools = Category.objects.create(name="Tools")
        books = Category.objects.create(name="Books")
        Resource.objects.create(
            owner=self.user,
            name="Drill",
            description="Electric drill",
            category=tools,
            is_available=True,
        )
        Resource.objects.create(
            owner=self.user,
            name="Novel",
            description="Fiction book",
            category=books,
            is_available=False,
        )
        url = reverse("resource-list")
        response = self.client.get(
            url, {"is_available": "true", "category": tools.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
