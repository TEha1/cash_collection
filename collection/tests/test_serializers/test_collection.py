from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from collection.models import Collection, CollectionLog, Task, CashCollector
from collection.serializers import CollectionSerializer, CollectionLogSerializer


class CollectionSerializerTests(TestCase):
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
        )

        # Create Collection
        self.collection = Collection.objects.create(
            task=self.task,
            amount=100.0,
            collected_at=timezone.now(),
            delivered=True,
            delivered_at=timezone.now(),
        )

    def test_collection_serializer(self):
        serializer = CollectionSerializer(instance=self.collection)
        data = serializer.data
        self.assertEqual(data["id"], self.collection.id)
        self.assertEqual(data["amount"], "100.00")
        self.assertEqual(data["delivered"], self.collection.delivered)
        self.assertEqual(data["task"]["id"], self.task.id)
        self.assertEqual(data["task"]["amount_due"], f"{self.task.amount_due:.2f}")
        self.assertEqual(data["task"]["customer_name"], self.task.customer_name)


class CollectionLogSerializerTests(TestCase):
    def setUp(self):
        # Create User
        self.user = User.objects.create_user(username="collector", password="password")

        # Create CashCollector
        self.collector = CashCollector.objects.create(
            user=self.user, balance=100.0, frozen=False
        )

        # Create CollectionLog
        self.collection_log = CollectionLog.objects.create(
            collector=self.collector, created=timezone.now(), status=True, amount=100.0
        )

    def test_collection_log_serializer(self):
        serializer = CollectionLogSerializer(instance=self.collection_log)
        data = serializer.data
        self.assertEqual(data["id"], self.collection_log.id)
        self.assertEqual(data["collector"], self.collector.id)
        self.assertEqual(data["status"], self.collection_log.status)
        self.assertEqual(data["amount"], "100.00")
