from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from collection.models import CashCollector, Manager
from collection.serializers import (
    UserSerializer,
    CashCollectorSerializer,
    ManagerSerializer,
)


class UserSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            first_name="Test",
            last_name="User",
            email="testuser@example.com",
        )

    def test_user_serializer(self):
        serializer = UserSerializer(instance=self.user)
        data = serializer.data
        self.assertEqual(data["id"], self.user.id)
        self.assertEqual(data["username"], self.user.username)
        self.assertEqual(data["first_name"], self.user.first_name)
        self.assertEqual(data["last_name"], self.user.last_name)
        self.assertEqual(data["email"], self.user.email)


class CashCollectorSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="collector", password="password")
        self.collector = CashCollector.objects.create(
            user=self.user,
            balance=100.0,
            frozen=False,
            last_collected_at=timezone.now(),
        )

    def test_cash_collector_serializer(self):
        serializer = CashCollectorSerializer(instance=self.collector)
        data = serializer.data
        self.assertEqual(data["id"], self.collector.id)
        self.assertEqual(data["user"]["id"], self.user.id)
        self.assertEqual(data["user"]["username"], self.user.username)
        self.assertEqual(data["balance"], "100.00")
        self.assertEqual(data["frozen"], self.collector.frozen)


class ManagerSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="manager", password="password")
        self.manager = Manager.objects.create(user=self.user)

    def test_manager_serializer(self):
        serializer = ManagerSerializer(instance=self.manager)
        data = serializer.data
        self.assertEqual(data["id"], self.manager.id)
        self.assertEqual(data["user"]["id"], self.user.id)
        self.assertEqual(data["user"]["username"], self.user.username)
