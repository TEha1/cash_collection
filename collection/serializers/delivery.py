from rest_framework import serializers

from collection.models import Task, Manager, Delivery


class TaskPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        collector = self.context.get("collector")
        return self.queryset.filter(cash_collector=collector)


class PaySerializer(serializers.Serializer):
    tasks = TaskPrimaryKeyRelatedField(
        many=True,
        queryset=Task.objects.filter(collected_at__isnull=True),
        required=False,
        write_only=True,
    )
    manager = serializers.PrimaryKeyRelatedField(
        queryset=Manager.objects.all(), write_only=True
    )


class DeliverySerializer(serializers.ModelSerializer):
    tasks = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Task.objects.all(), required=False, write_only=True
    )

    class Meta:
        model = Delivery
        fields = ["id", "collector", "manager", "delivered_at", "collections", "tasks"]
