from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from collection.models import Task, CashCollector

from django.conf import settings


class CollectionViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create user and cash collector
        self.user = User.objects.create_user(username="collector", password="password")
        self.collector = CashCollector.objects.create(user=self.user, frozen=False)

        # Create customer and task
        self.task = Task.objects.create(
            cash_collector=self.collector,
            amount_due=100.0,
            customer_name="John Doe",
            customer_address="123 Main St",
            amount_due_at=timezone.now(),
        )

        # Create token
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_create_collection_success(self):
        url = reverse("collection-list")
        data = {"amount": 100.0, "task": self.task.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["amount"], f"{data['amount']:.2f}")
        self.assertEqual(response.data["task"]["id"], self.task.id)

    def test_create_collection_task_already_collected(self):
        self.task.collected_at = timezone.now()
        self.task.save(update_fields=["collected_at"])
        url = reverse("collection-list")
        data = {
            "amount": 100.0,
            "task": self.task.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Task already collected.")

    def test_create_collection_frozen_collector(self):
        self.collector.frozen = True
        self.collector.balance = settings.CASH_LIMIT + 1
        self.collector.last_collected_at = timezone.now() - timedelta(
            days=settings.DAYS_LIMIT + 1
        )
        self.collector.save()
        url = reverse("collection-list")
        data = {
            "amount": 100.0,
            "task": self.task.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"], "Your are frozen, you can't collect currently."
        )

    def test_create_collection_invalid_data(self):
        url = reverse("collection-list")
        data = {
            "amount": "invalid",
            "task": "invalid",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
