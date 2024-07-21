from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from collection.models import Task, Manager, Delivery, CashCollector, Collection
from collection.serializers import (
    TaskPrimaryKeyRelatedField,
    PaySerializer,
    DeliverySerializer,
)


class TaskPrimaryKeyRelatedFieldTests(TestCase):
    def setUp(self):
        # Create User
        self.user = User.objects.create_user(username="collector", password="password")
        self.another_user = User.objects.create_user(
            username="another_user", password="password"
        )

        # Create CashCollector and Manager
        self.collector = CashCollector.objects.create(user=self.user)
        self.another_collector = CashCollector.objects.create(user=self.another_user)

        # Create Task
        self.task1 = Task.objects.create(
            cash_collector=self.collector,
            customer_name="John Doe",
            customer_address="123 Main St",
            amount_due=100.0,
            amount_due_at=timezone.now(),
        )
        self.task2 = Task.objects.create(
            cash_collector=self.another_collector,
            customer_name="Jane Doe",
            customer_address="456 Elm St",
            amount_due=200.0,
            amount_due_at=timezone.now(),
            collected_at=timezone.now(),
        )

    def test_task_primary_key_related_field(self):
        field = TaskPrimaryKeyRelatedField(queryset=Task.objects.all(), many=True)
        context = {"collector": self.collector}
        field.root._context = context
        queryset = field.child_relation.get_queryset()
        self.assertIn(self.task1, queryset)
        self.assertNotIn(self.task2, queryset)


class PaySerializerTests(TestCase):
    def setUp(self):
        # Create User
        self.user = User.objects.create_user(username="collector", password="password")
        self.manager_user = User.objects.create_user(
            username="manager", password="password"
        )

        # Create CashCollector and Manager
        self.collector = CashCollector.objects.create(user=self.user, frozen=False)
        self.manager = Manager.objects.create(user=self.manager_user)

        # Create Task
        self.task = Task.objects.create(
            cash_collector=self.collector,
            customer_name="John Doe",
            customer_address="123 Main St",
            amount_due=100.0,
            amount_due_at=timezone.now(),
        )

    def test_pay_serializer_valid(self):
        data = {"tasks": [self.task.id], "manager": self.manager.id}
        context = {"collector": self.collector}
        serializer = PaySerializer(data=data, context=context)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["tasks"], [self.task])
        self.assertEqual(serializer.validated_data["manager"], self.manager)

    def test_pay_serializer_invalid(self):
        data = {"tasks": [self.task.id], "manager": 999}  # Invalid manager ID
        context = {"collector": self.collector}
        serializer = PaySerializer(data=data, context=context)
        self.assertFalse(serializer.is_valid())
        self.assertIn("manager", serializer.errors)


class DeliverySerializerTests(TestCase):
    def setUp(self):
        # Create User
        self.user = User.objects.create_user(username="collector", password="password")
        self.manager_user = User.objects.create_user(
            username="manager", password="password"
        )

        # Create CashCollector and Manager
        self.collector = CashCollector.objects.create(user=self.user, frozen=False)
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
            amount=100.0,
            collected_at=timezone.now(),
            delivered=True,
            delivered_at=timezone.now(),
        )

        # Create Delivery
        self.delivery = Delivery.objects.create(
            collector=self.collector, manager=self.manager
        )
        self.delivery.collections.add(self.collection)

    def test_delivery_serializer(self):
        serializer = DeliverySerializer(instance=self.delivery)
        data = serializer.data
        self.assertEqual(data["id"], self.delivery.id)
        self.assertEqual(data["collector"], self.collector.id)
        self.assertEqual(data["manager"], self.manager.id)
        self.assertIn(self.collection.id, data["collections"])
