from django.test import TestCase
from django.contrib.auth.models import User
from collection.models import Collection, CollectionLog, CashCollector, Task
from django.utils import timezone
from decimal import Decimal


class CollectionModelTests(TestCase):
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

    def test_collection_creation(self):
        collection = Collection.objects.create(
            task=self.task,
            amount=Decimal("50.00"),
            collected_at=timezone.now(),
            delivered=True,
            delivered_at=timezone.now(),
        )
        self.assertEqual(collection.task, self.task)
        self.assertEqual(collection.amount, Decimal("50.00"))
        self.assertTrue(collection.delivered)
        self.assertIsNotNone(collection.collected_at)
        self.assertIsNotNone(collection.delivered_at)

    def test_collection_str(self):
        collection = Collection.objects.create(
            task=self.task,
            amount=Decimal("50.00"),
            collected_at=timezone.now(),
            delivered=True,
            delivered_at=timezone.now(),
        )
        self.assertEqual(str(collection), f"{self.task} - 50.00")


class CollectionLogModelTests(TestCase):
    def setUp(self):
        # Create User
        self.user = User.objects.create_user(username="collector", password="password")

        # Create CashCollector
        self.collector = CashCollector.objects.create(
            user=self.user, balance=100.0, frozen=False
        )

    def test_collection_log_creation(self):
        collection_log = CollectionLog.objects.create(
            collector=self.collector,
            amount=Decimal("50.00"),
            created=timezone.now(),
            status=True,
        )
        self.assertEqual(collection_log.collector, self.collector)
        self.assertEqual(collection_log.amount, Decimal("50.00"))
        self.assertTrue(collection_log.status)
        self.assertIsNotNone(collection_log.created)

    def test_collection_log_str(self):
        collection_log = CollectionLog.objects.create(
            collector=self.collector,
            amount=Decimal("50.00"),
            created=timezone.now(),
            status=True,
        )
        self.assertEqual(
            str(collection_log), f"{self.collector} - {collection_log.created}"
        )
