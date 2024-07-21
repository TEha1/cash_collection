from rest_framework import serializers

from collection.models import Task
from collection.serializers import CashCollectorSerializer


class TaskSerializer(serializers.ModelSerializer):
    cash_collector = CashCollectorSerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "customer_name",
            "customer_address",
            "amount_due",
            "amount_due_at",
            "collected_at",
            "collected_amount",
            "cash_collector",
        ]
