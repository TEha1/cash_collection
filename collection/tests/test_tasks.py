from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.utils import timezone

from collection.models import CashCollector
from collection.tasks import update_frozen_status


class UpdateFrozenStatusTaskTests(TestCase):
    def setUp(self):
        # Create Users
        self.user1 = User.objects.create_user(
            username="collector1", password="password"
        )
        self.user2 = User.objects.create_user(
            username="collector2", password="password"
        )
        self.user3 = User.objects.create_user(
            username="collector3", password="password"
        )

        # Create CashCollectors
        self.collector1 = CashCollector.objects.create(
            user=self.user1,
            balance=2000,
            last_collected_at=timezone.now() - timedelta(days=3),
            frozen=False,
        )
        self.collector2 = CashCollector.objects.create(
            user=self.user2,
            balance=500,
            last_collected_at=timezone.now() - timedelta(days=3),
            frozen=False,
        )
        self.collector3 = CashCollector.objects.create(
            user=self.user3,
            balance=2000,
            last_collected_at=timezone.now() - timedelta(days=1),
            frozen=False,
        )
        self.settings = override_settings(CASH_LIMIT=1000, DAYS_LIMIT=2)
        self.settings.enable()

    def tearDown(self):
        self.settings.disable()

    def test_update_frozen_status_task(self):
        update_frozen_status()

        self.collector1.refresh_from_db()
        self.collector2.refresh_from_db()
        self.collector3.refresh_from_db()

        self.assertTrue(self.collector1.frozen, "Collector 1 should be frozen")
        self.assertFalse(self.collector2.frozen, "Collector 2 should not be frozen")
        self.assertFalse(self.collector3.frozen, "Collector 3 should not be frozen")

    def test_update_frozen_status_task_no_eligible_collectors(self):
        # Set all collectors to be not eligible for freezing
        self.collector1.balance = 500
        self.collector1.save()
        self.collector3.last_collected_at = timezone.now()
        self.collector3.save()

        update_frozen_status()

        self.collector1.refresh_from_db()
        self.collector2.refresh_from_db()
        self.collector3.refresh_from_db()

        self.assertFalse(self.collector1.frozen, "Collector 1 should not be frozen")
        self.assertFalse(self.collector2.frozen, "Collector 2 should not be frozen")
        self.assertFalse(self.collector3.frozen, "Collector 3 should not be frozen")
