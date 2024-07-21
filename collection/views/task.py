from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from collection.models import Task
from collection.permissions import IsCashCollector, IsManagerOrCollector
from collection.serializers import TaskSerializer


class TaskViewSet(ReadOnlyModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated, IsManagerOrCollector)

    def get_queryset(self):
        if cash_collector := getattr(self.request.user, "cash_collector", None):
            # Only listing the collected tasks for a specific collector
            tasks = Task.objects.filter(
                cash_collector=cash_collector, collected_at__isnull=False
            )
        else:
            tasks = Task.objects.all()
        return tasks.select_related("cash_collector").order_by("amount_due_at")

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated, IsCashCollector],
    )
    def next_task(self, request):
        cash_collect = request.user.cash_collector
        next_task = (
            Task.objects.filter(cash_collector=cash_collect, collected_at__isnull=True)
            .order_by("amount_due_at")
            .first()
        )
        if not next_task:
            return Response(
                {"details": _("No tasks yet")}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(next_task)
        return Response(serializer.data)
