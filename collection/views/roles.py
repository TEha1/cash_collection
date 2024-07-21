from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from collection.models import Manager, CashCollector, CollectionLog
from collection.permissions import IsManagerOrCollector
from collection.serializers import (
    ManagerSerializer,
    CashCollectorSerializer,
    CollectionLogSerializer,
)


class ManagerViewSet(ReadOnlyModelViewSet):
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer


class CashCollectorViewSet(ReadOnlyModelViewSet):
    queryset = CashCollector.objects.all()
    serializer_class = CashCollectorSerializer
    permission_classes = (IsAuthenticated, IsManagerOrCollector)

    def get_queryset(self):
        queryset = super().get_queryset()
        frozen = self.request.query_params.get("frozen")
        if frozen == "true":
            queryset = queryset.filter(frozen=True)
        elif frozen == "false":
            queryset = queryset.filter(frozen=False)
        return queryset

    @action(detail=True, methods=["get"], url_path="status", url_name="status")
    def status(self, request, pk=None):
        collector: CashCollector = self.get_object()
        return Response({"frozen": collector.frozen})

    @action(detail=True, methods=["get"], url_path="status-log")
    def status_log(self, *args, **kwargs):
        collector: CashCollector = self.get_object()
        logs = CollectionLog.objects.filter(collector=collector).order_by("-created")
        serializer = CollectionLogSerializer(logs, many=True)
        return Response(serializer.data)
