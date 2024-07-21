from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.utils import timezone

from collection.models import CashCollector, Manager, CollectionLog


class CashCollectorModelTests(TestCase):
    def setUp(self):
        # Create User
        self.user = User.objects.create_user(username="collector", password="password")

        # Create CashCollector
        self.collector = CashCollector.objects.create(
            user=self.user, balance=Decimal("100.00"), frozen=False
        )
        self.settings = override_settings(CASH_LIMIT=1000, DAYS_LIMIT=2)
        self.settings.enable()

    def tearDown(self):
        self.settings.disable()

    def test_cash_collector_creation(self):
        self.assertEqual(self.collector.user, self.user)
        self.assertEqual(self.collector.balance, Decimal("100.00"))
        self.assertFalse(self.collector.frozen)

    def test_update_frozen_status_not_frozen(self):
        self.collector.last_collected_at = timezone.now() - timedelta(days=1)
        self.collector.save()
        self.collector.update_frozen_status()
        self.assertFalse(self.collector.frozen)

    def test_update_frozen_status_frozen(self):
        self.collector.balance = Decimal("2000.00")
        self.collector.last_collected_at = timezone.now() - timedelta(days=3)
        self.collector.save()
        self.collector.update_frozen_status()
        self.assertTrue(self.collector.frozen)

    def test_update_balance_and_collection_time(self):
        amount = Decimal("200.00")
        self.collector.update_balance_and_collection_time(amount)
        self.assertEqual(self.collector.balance, Decimal("300.00"))
        self.assertIsNotNone(self.collector.last_collected_at)

    def test_create_status_log(self):
        amount = Decimal("50.00")
        self.collector.create_status_log(amount)
        log = CollectionLog.objects.get(collector=self.collector)
        self.assertEqual(log.amount, amount)
        self.assertEqual(log.collector, self.collector)
        self.assertEqual(log.status, self.collector.frozen)

    def test_cash_collector_str(self):
        self.assertEqual(str(self.collector), f"{self.user} - 100.00")


class ManagerModelTests(TestCase):
    def setUp(self):
        # Create User
        self.user = User.objects.create_user(username="manager", password="password")

        # Create Manager
        self.manager = Manager.objects.create(user=self.user)

    def test_manager_creation(self):
        self.assertEqual(self.manager.user, self.user)

    def test_manager_str(self):
        self.assertEqual(str(self.manager), f"{self.user} - {self.manager.pk}")
