from rest_framework import serializers

from collection.models import Collection, CollectionLog


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ["id", "task", "amount", "collected_at", "delivered"]

    def to_representation(self, instance):
        from collection.serializers import TaskSerializer

        data = super().to_representation(instance)
        data["task"] = TaskSerializer(instance.task).data
        return data


class CollectionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionLog
        fields = ["id", "collector", "created", "status", "amount"]
