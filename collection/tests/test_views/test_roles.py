from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from collection.models import Manager, CashCollector, CollectionLog
from django.utils import timezone


class ManagerViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="manager", password="password")
        self.manager = Manager.objects.create(user=self.user)
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_manager_list(self):
        url = reverse("manager-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data["results"]), 1)
        self.assertEqual(response_data["results"][0]["user"]["username"], "manager")


class CashCollectorViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="collector", password="password")
        self.unauthorized_user = User.objects.create_user(
            username="unauthorized_user", password="password"
        )
        self.collector = CashCollector.objects.create(user=self.user, frozen=False)
        self.log = CollectionLog.objects.create(
            collector=self.collector,
            created=timezone.now(),
            status=self.collector.frozen,
            amount=10,
        )
        self.token = Token.objects.create(user=self.user)
        self.unauthorized_token = Token.objects.create(user=self.unauthorized_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_cash_collector_list(self):
        url = reverse("cash_collector-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["user"]["username"], "collector")

    def test_cash_collector_list_with_unauthorized_user(self):
        url = reverse("cash_collector-list")
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.unauthorized_token.key}"
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(
            response.json(),
            {"detail": "You do not have permission to perform this action."},
        )

    def test_cash_collector_list_frozen(self):
        self.collector.frozen = True
        self.collector.save()
        url = reverse("cash_collector-list") + "?frozen=true"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(len(response_data["results"]), 1)
        self.assertEqual(response_data["results"][0]["user"]["username"], "collector")
        self.assertTrue(response_data["results"][0]["frozen"])

    def test_cash_collector_list_unfrozen(self):
        url = reverse("cash_collector-list") + "?frozen=false"
        response = self.client.get(url)
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_data["results"]), 1)
        self.assertEqual(response_data["results"][0]["user"]["username"], "collector")
        self.assertFalse(response_data["results"][0]["frozen"])

    def test_cash_collector_status(self):
        url = reverse("cash_collector-status", kwargs={"pk": self.collector.id})
        response = self.client.get(url)
        response_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data["frozen"], self.collector.frozen)

    def test_cash_collector_status_log(self):
        url = reverse("cash_collector-status-log", kwargs={"pk": self.collector.id})
        response = self.client.get(url)
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_data), 1)
        self.assertEqual(response_data[0]["collector"], self.collector.id)

    def test_cash_collector_status_log_empty(self):
        self.log.delete()
        url = reverse("cash_collector-status-log", kwargs={"pk": self.collector.id})
        response = self.client.get(url)
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_data), 0)
