from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import User


class UserAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_success(self):
        data = {
            "nom": "Test User",
            "email": "test@example.com",
            "password": "password123"
        }
        response = self.client.post("/api/auth/register/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["email"], "test@example.com")
        self.assertEqual(response.data["user"]["nom"], "Test User")
        self.assertTrue(User.objects.filter(email="test@example.com").exists())

    def test_register_duplicate_email(self):
        User.objects.create_user(
            email="existing@example.com",
            password="password123",
            nom="Existing User"
        )
        data = {
            "nom": "Another User",
            "email": "existing@example.com",
            "password": "password123"
        }
        response = self.client.post("/api/auth/register/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Cet email existe déjà.")

    def test_register_short_password(self):
        data = {
            "nom": "Test User",
            "email": "test@example.com",
            "password": "short"
        }
        response = self.client.post("/api/auth/register/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Le mot de passe doit contenir au moins 8 caractères.")

    def test_profile_endpoints(self):
        user = User.objects.create_user(
            email="profile@example.com",
            password="password123",
            nom="Profile User"
        )
        login_res = self.client.post("/api/auth/login/", {
            "email": "profile@example.com",
            "password": "password123"
        }, format="json")
        token = login_res.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        # Both /api/auth/me/ and /api/users/me/ should work
        res1 = self.client.get("/api/auth/me/")
        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        self.assertEqual(res1.data["email"], "profile@example.com")

        res2 = self.client.get("/api/users/me/")
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.data["email"], "profile@example.com")
