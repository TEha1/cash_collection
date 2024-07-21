from rest_framework import serializers
from django.contrib.auth.models import User
from collection.models import CashCollector, Manager


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"]


class CashCollectorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = CashCollector
        fields = ["id", "user", "balance", "frozen", "last_collected_at"]


class ManagerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Manager
        fields = ["id", "user"]
