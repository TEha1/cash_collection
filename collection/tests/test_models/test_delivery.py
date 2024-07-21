from django.test import TestCase
from django.contrib.auth.models import User
from collection.models import Delivery, CashCollector, Manager, Collection, Task
from django.utils import timezone
from decimal import Decimal


class DeliveryModelTests(TestCase):
    def setUp(self):
        # Create Users
        self.collector_user = User.objects.create_user(
            username="collector", password="password"
        )
        self.manager_user = User.objects.create_user(
            username="manager", password="password"
        )

        # Create CashCollector and Manager
        self.collector = CashCollector.objects.create(
            user=self.collector_user, balance=100.0, frozen=False
        )
        self.manager = Manager.objects.create(user=self.manager_user)

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
            amount=Decimal("50.00"),
            collected_at=timezone.now(),
            delivered=False,
        )

    def test_delivery_creation(self):
        delivery = Delivery.objects.create(
            collector=self.collector, manager=self.manager
        )
        delivery.collections.add(self.collection)
        self.assertEqual(delivery.collector, self.collector)
        self.assertEqual(delivery.manager, self.manager)
        self.assertIn(self.collection, delivery.collections.all())
        self.assertIsNotNone(delivery.delivered_at)

    def test_delivery_str(self):
        delivery = Delivery.objects.create(
            collector=self.collector, manager=self.manager
        )
        self.assertEqual(str(delivery), f"{self.collector} - {delivery.delivered_at}")
