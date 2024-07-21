from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import ValidationError as Http400
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from collection.models import Collection, Task, CashCollector
from collection.permissions import IsCashCollector
from collection.serializers import CollectionSerializer


class CollectionViewSet(GenericViewSet, CreateModelMixin):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAuthenticated, IsCashCollector]

    def create(self, request, *args, **kwargs):
        collector: CashCollector = request.user.cash_collector
        collector.update_frozen_status()
        if collector.frozen:
            raise Http400({"detail": "Your are frozen, you can't collect currently."})

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        amount = validated_data["amount"]
        task: Task = validated_data["task"]
        if task.collected_at:
            return Response(
                {"detail": "Task already collected."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()
        with transaction.atomic():
            collector.update_balance_and_collection_time(amount=amount)
            collector.update_frozen_status()
            collector.create_status_log(amount=amount)
            task.update_collected_at()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
