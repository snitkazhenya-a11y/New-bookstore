from datetime import timedelta
from django.contrib.sessions.models import Session
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from accounts.tasks import cleanup_expired_sessions

User = get_user_model()


class AccountsAPITests(APITestCase):

    def setUp(self):
        self.token_url = reverse("token_obtain_pair")
        self.refresh_url = reverse("token_refresh")
        self.user_data = {"username": "apiuser", "password": "strongpassword123"}
        self.user = User.objects.create_user(**self.user_data)

    def test_obtain_jwt_token(self):
        """Тест: отримання JWT токенів за логіном та паролем"""
        response = self.client.post(self.token_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_obtain_jwt_token_invalid_credentials(self):
        """Тест: помилка отримання токена з невірним паролем"""
        invalid_data = {"username": "apiuser", "password": "wrongpassword"}
        response = self.client.post(self.token_url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_jwt_token(self):
        """Тест: оновлення access токена за допомогою refresh токена"""
        token_response = self.client.post(self.token_url, self.user_data)
        refresh_token = token_response.data["refresh"]

        response = self.client.post(self.refresh_url, {"refresh": refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_refresh_jwt_token_invalid(self):
        """Тест: помилка оновлення токена з невалідним/хибним refresh токеном"""
        response = self.client.post(
            self.refresh_url, {"refresh": "invalid-refresh-token-string"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cleanup_expired_sessions_task(self):
        """Тест: Celery-задача видаляє лише прострочені сесії"""
        now = timezone.now()
        Session.objects.create(
            session_key="expired_sess",
            session_data="",
            expire_date=now - timedelta(days=1),
        )
        Session.objects.create(
            session_key="active_sess",
            session_data="",
            expire_date=now + timedelta(days=1),
        )

        result = cleanup_expired_sessions.run()

        self.assertIn("cleaned up", result)
        self.assertFalse(Session.objects.filter(session_key="expired_sess").exists())
        self.assertTrue(Session.objects.filter(session_key="active_sess").exists())
