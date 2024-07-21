from django.db.models import Sum
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError as Http400

from collection.models import Collection, Delivery
from collection.permissions import IsCashCollector
from collection.serializers import DeliverySerializer, PaySerializer


class DeliveryCreateAPIView(CreateAPIView):
    queryset = Delivery.objects.all()
    serializer_class = PaySerializer
    permission_classes = [IsAuthenticated, IsCashCollector]

    def post(self, request, *args, **kwargs):
        collector = request.user.cash_collector
        data = self._prepare_data(request.data, collector)
        serializer = self._validate_serializer(data, collector)
        deliveries = self._process_tasks(serializer.validated_data, collector)
        return Response(
            DeliverySerializer(deliveries, many=True).data,
            status=status.HTTP_201_CREATED,
        )

    @staticmethod
    def _prepare_data(data, collector):
        data = data.copy()
        data.update(collector=collector.id)
        return data

    def _validate_serializer(self, data, collector):
        serializer = self.get_serializer(data=data, context={"collector": collector})
        serializer.is_valid(raise_exception=True)
        return serializer

    def _process_tasks(self, validated_data, collector):
        tasks = validated_data.get("tasks")
        manager = validated_data["manager"]

        if tasks:
            return self._process_tasks_with_items(tasks, collector, manager)
        else:
            return self._process_tasks_without_items(collector, manager)

    def _process_tasks_with_items(self, tasks, collector, manager):
        deliveries = []
        for task in tasks:
            collections = self._get_collections_for_task(task)
            if not collections:
                continue
            delivery = self._create_delivery(collector, manager, collections)
            deliveries.append(delivery)
            collector.balance -= self._calculate_total_collected_amount(collections)
            self._update_collections_as_delivered(collections)
        collector.save(update_fields=["balance"])
        return deliveries

    def _process_tasks_without_items(self, collector, manager):
        collections = self._get_collections_for_collector(collector)
        if not collections:
            raise Http400({"details": _("Collection does not exist")})
        delivery = self._create_delivery(collector, manager, collections)
        self._update_collections_as_delivered(collections)
        collector.balance = 0
        collector.save(update_fields=["balance"])
        return [delivery]

    @staticmethod
    def _get_collections_for_task(task):
        return Collection.objects.filter(task=task, delivered=False)

    @staticmethod
    def _get_collections_for_collector(collector):
        return Collection.objects.filter(
            task__cash_collector=collector, delivered=False
        )

    @staticmethod
    def _update_collections_as_delivered(collections):
        collections.update(delivered=True, delivered_at=timezone.now())

    @staticmethod
    def _create_delivery(collector, manager, collections):
        delivery = Delivery.objects.create(collector=collector, manager=manager)
        delivery.collections.set(collections)
        return delivery

    @staticmethod
    def _calculate_total_collected_amount(collections):
        return collections.aggregate(collected=Sum("amount"))["collected"] or 0
