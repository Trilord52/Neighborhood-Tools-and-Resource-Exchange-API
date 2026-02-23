from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model


User = get_user_model()


class AuthTests(APITestCase):
    def test_register_and_login(self):
        register_url = reverse("register")
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "strongpassword123",
        }
        response = self.client.post(register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        token = response.data.get("token")
        self.assertIsNotNone(token)

        login_url = reverse("login")
        login_response = self.client.post(
            login_url,
            {"username": "testuser", "password": "strongpassword123"},
            format="json",
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn("token", login_response.data)

    def test_login_invalid_credentials(self):
        user = User.objects.create_user(
            username="testuser2", email="test2@example.com", password="password123"
        )
        login_url = reverse("login")
        response = self.client.post(
            login_url,
            {"username": user.username, "password": "wrongpassword"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_me_requires_authentication(self):
        me_url = reverse("me")
        response = self.client.get(me_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_with_token(self):
        user = User.objects.create_user(
            username="meuser", email="me@example.com", password="password123"
        )
        login_url = reverse("login")
        login_response = self.client.post(
            login_url,
            {"username": "meuser", "password": "password123"},
            format="json",
        )
        token = login_response.data["token"]
        me_url = reverse("me")
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.get(me_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "meuser")
