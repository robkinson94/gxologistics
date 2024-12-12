from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import CustomUser
from django.shortcuts import get_object_or_404
from .utils import email_verification_token
from .models import Team
from rest_framework_simplejwt.tokens import RefreshToken


class RegisterUserViewTestCase(APITestCase):
    def test_register_user_success(self):
        url = reverse("register")
        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "StrongP@ssw0rd",
            "confirm_password": "StrongP@ssw0rd",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CustomUser.objects.filter(username="testuser").exists())

    def test_register_user_password_mismatch(self):
        url = reverse("register")
        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "password123",
            "confirm_password": "password321",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)


class VerifyEmailViewTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123",
            is_active=False
        )
        self.token = email_verification_token.make_token(self.user)

    def test_verify_email_success(self):
        url = reverse("email-verify")
        data = {"token": self.token, "uid": self.user.id}
        response = self.client.post(url, data)
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.is_active)

    def test_verify_email_invalid_token(self):
        url = reverse("email-verify")
        data = {"token": "invalidtoken", "uid": self.user.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)


class TeamCRUDViewTestCase(APITestCase):
    def setUp(self):
        self.admin_user = CustomUser.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="adminpassword",
            is_admin=True
        )
        self.client.force_authenticate(user=self.admin_user)

    def test_create_team_success(self):
        url = reverse("team-list-create")
        data = {"name": "Team Alpha"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Team.objects.filter(name="Team Alpha").exists())

    def test_create_team_unauthorized(self):
        self.client.logout()
        url = reverse("team-list-create")
        data = {"name": "Team Alpha"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)