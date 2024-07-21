from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from .models import CashCollector


def update_frozen_status():
    collectors = CashCollector.objects.filter(balance__gte=settings.CASH_LIMIT)
    for collector in collectors:
        if (
            collector.last_collected_at + timedelta(days=settings.DAYS_LIMIT)
            <= timezone.now()
        ):
            collector.frozen = True
        else:
            collector.frozen = False
    CashCollector.objects.bulk_update(collectors, fields=["frozen"])
