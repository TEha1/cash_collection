from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from collection.models import Task, CashCollector


class TaskViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create users
        self.user = User.objects.create_user(username="collector", password="password")
        self.another_user = User.objects.create_user(
            username="another_collector", password="password"
        )
        self.unauthorized_user = User.objects.create_user(
            username="unauthorized_user", password="password"
        )

        # Create CashCollectors
        self.collector = CashCollector.objects.create(user=self.user, frozen=False)
        self.another_collector = CashCollector.objects.create(
            user=self.another_user, frozen=False
        )

        # Create Tasks
        self.task1 = Task.objects.create(
            customer_name="John Doe",
            customer_address="123 Main St",
            cash_collector=self.collector,
            amount_due=100.0,
            amount_due_at=timezone.now(),
            collected_at=timezone.now(),
        )
        self.task2 = Task.objects.create(
            customer_name="John Doe",
            customer_address="122 Main St",
            cash_collector=self.collector,
            collected_at=None,
            amount_due=200.0,
            amount_due_at=timezone.now(),
        )
        self.task3 = Task.objects.create(
            customer_name="John Doe",
            customer_address="143 Main St",
            cash_collector=self.another_collector,
            collected_at=timezone.now(),
            amount_due=300.0,
            amount_due_at=timezone.now(),
        )

        # Create Token
        self.token = Token.objects.create(user=self.user)
        self.another_token = Token.objects.create(user=self.another_user)
        self.unauthorized_token = Token.objects.create(user=self.unauthorized_user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_task_list_for_cash_collector(self):
        url = reverse("task-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data["results"]), 1)
        self.assertEqual(
            response_data["results"][0]["amount_due"], f"{self.task1.amount_due:.2f}"
        )
        self.assertIsNotNone(response_data["results"][0]["collected_at"])

    def test_task_list_for_unauthorized(self):
        url = reverse("task-list")
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.unauthorized_token.key}"
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(
            response.json(),
            {"detail": "You do not have permission to perform this action."},
        )

    def test_task_list_for_another_cash_collector(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.another_token}")
        url = reverse("task-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data["results"]), 1)
        self.assertEqual(
            response_data["results"][0]["amount_due"], f"{self.task3.amount_due:.2f}"
        )
        self.assertIsNotNone(response_data["results"][0]["collected_at"])

    def test_next_task_for_cash_collector(self):
        url = reverse("task-next-task")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data["amount_due"], f"{self.task2.amount_due:.2f}")

    def test_next_task_for_another_cash_collector(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.another_token.key}")
        url = reverse("task-next-task")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(response.data, {"details": "No tasks yet"})

    def test_task_list_for_admin(self):
        admin_user = User.objects.create_superuser(
            username="admin", password="password", email="admin@example.com"
        )
        admin_token = Token.objects.create(user=admin_user).key
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {admin_token}")
        url = reverse("task-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)
