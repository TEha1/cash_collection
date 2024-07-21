from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from collection.models import CashCollector, Task, Collection


class TaskModelTests(TestCase):
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
            amount_due_at=timezone.now() + timedelta(days=1),
        )

        # Create Collections
        self.collection1 = Collection.objects.create(
            task=self.task,
            amount=Decimal("50.00"),
            collected_at=timezone.now(),
            delivered=False,
        )
        self.collection2 = Collection.objects.create(
            task=self.task,
            amount=Decimal("50.00"),
            collected_at=timezone.now(),
            delivered=False,
        )

    def test_task_creation(self):
        self.assertEqual(self.task.cash_collector, self.collector)
        self.assertEqual(self.task.customer_name, "John Doe")
        self.assertEqual(self.task.customer_address, "123 Main St")
        self.assertEqual(self.task.amount_due, Decimal("100.00"))
        self.assertIsNone(self.task.collected_at)

    def test_task_str(self):
        self.assertEqual(str(self.task), "John Doe - 100.00")

    def test_collected_amount_property(self):
        self.assertEqual(self.task.collected_amount, Decimal("100.00"))

    def test_update_collected_at(self):
        self.task.update_collected_at()
        self.assertIsNotNone(self.task.collected_at)

    def test_update_collected_at_not_enough_collected(self):
        # Create another task with less collected amount
        task2 = Task.objects.create(
            cash_collector=self.collector,
            customer_name="Jane Doe",
            customer_address="456 Elm St",
            amount_due=200.0,
            amount_due_at=timezone.now() + timedelta(days=1),
        )
        Collection.objects.create(
            task=task2,
            amount=Decimal("50.00"),
            collected_at=timezone.now(),
            delivered=False,
        )
        task2.update_collected_at()
        self.assertIsNone(task2.collected_at)
