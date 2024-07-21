from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from collection.models import Collection, CashCollector, Task, Manager


class DeliveryCreateAPIViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create users
        self.user = User.objects.create_user(username="collector", password="password")
        self.manager_user = User.objects.create_user(
            username="manager", password="password"
        )
        self.unauthorized_user = User.objects.create_user(
            username="unauthorized_user", password="password"
        )

        # Create CashCollector and Manager
        self.collector = CashCollector.objects.create(
            user=self.user, frozen=False, balance=1000
        )
        self.manager = Manager.objects.create(user=self.manager_user)

        # Create Tasks
        self.task1 = Task.objects.create(
            customer_name="John Doe",
            customer_address="123 Main St",
            amount_due=100.0,
            amount_due_at=timezone.now(),
            cash_collector=self.collector,
        )
        self.task2 = Task.objects.create(
            customer_name="John Doe",
            customer_address="123 Main St",
            cash_collector=self.collector,
            amount_due_at=timezone.now(),
            amount_due=200.0,
        )

        # Create Collections
        self.collection1 = Collection.objects.create(task=self.task1, amount=100.0)
        self.collection2 = Collection.objects.create(task=self.task2, amount=200.0)

        # Create Token
        self.token = Token.objects.create(user=self.user)
        self.unauthorized_token = Token.objects.create(user=self.unauthorized_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_create_delivery_with_unauthorized_user(self):
        url = reverse("pay")
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.unauthorized_token.key}"
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(
            response.json(),
            {"detail": "You do not have permission to perform this action."},
        )

    def test_create_delivery_with_tasks(self):
        url = reverse("pay")
        data = {"manager": self.manager.id, "tasks": [self.task1.id, self.task2.id]}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = response.json()
        self.assertEqual(len(response_data), 2)
        self.assertListEqual(response_data[0]["collections"], [self.collection1.id])
        self.assertListEqual(response_data[1]["collections"], [self.collection2.id])

    def test_create_delivery_without_tasks(self):
        url = reverse("pay")
        data = {"manager": self.manager.id, "tasks": []}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = response.json()
        self.assertEqual(len(response_data), 1)
        self.assertListEqual(
            response_data[0]["collections"], [self.collection2.id, self.collection1.id]
        )

    def test_create_delivery_task_already_collected(self):
        self.collection1.delivered = True
        self.collection1.save()
        url = reverse("pay")
        data = {"manager": self.manager.id, "tasks": [self.task1.id, self.task2.id]}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = response.json()
        self.assertEqual(len(response_data), 1)
        self.assertEqual(response_data[0]["collections"], [self.collection2.id])

    def test_create_delivery_for_collected_tasks(self):
        Collection.objects.all().update(delivered=True)
        url = reverse("pay")
        data = {"manager": self.manager.id, "tasks": []}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertDictEqual(response_data, {"details": "Collection does not exist"})

    def test_create_delivery_invalid_data(self):
        url = reverse("pay")
        data = {"manager": "invalid", "tasks": ["invalid"]}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
