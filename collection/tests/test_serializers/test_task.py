from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from collection.models import CashCollector, Task
from collection.serializers import TaskSerializer


class TaskSerializerTests(TestCase):
    def setUp(self):
        # Create User
        self.user = User.objects.create_user(username="collector", password="password")

        # Create CashCollector
        self.collector = CashCollector.objects.create(
            user=self.user, balance=100.0, frozen=False
        )

        # Create Task
        self.task = Task.objects.create(
            cash_collector=self.collector,
            customer_name="John Doe",
            customer_address="123 Main St",
            amount_due=100.0,
            amount_due_at=timezone.now(),
            collected_at=timezone.now(),
        )

    def test_task_serializer(self):
        serializer = TaskSerializer(instance=self.task)
        data = serializer.data
        self.assertEqual(data["id"], self.task.id)
        self.assertEqual(data["customer_name"], self.task.customer_name)
        self.assertEqual(data["customer_address"], self.task.customer_address)
        self.assertEqual(data["amount_due"], "100.00")
        self.assertIsNone(data["collected_amount"])
        self.assertEqual(data["cash_collector"]["id"], self.collector.id)
        self.assertEqual(data["cash_collector"]["user"]["id"], self.user.id)
        self.assertEqual(data["cash_collector"]["user"]["username"], self.user.username)

    def test_task_serializer_with_collected_amount(self):
        # Update the task with a collected amount
        self.task.collected_amount = Decimal("50.00")
        self.task.save()

        serializer = TaskSerializer(instance=self.task)
        data = serializer.data
        self.assertEqual(data["collected_amount"], Decimal("50.00"))
