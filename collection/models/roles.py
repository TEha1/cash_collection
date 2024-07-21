from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
from django.utils import timezone


class CashCollector(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="cash_collector",
        verbose_name=_("user"),
    )
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name=_("balance"),
    )
    frozen = models.BooleanField(
        default=False,
        verbose_name=_("frozen"),
    )
    last_collected_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("last collected date time"),
    )

    class Meta:
        verbose_name = _("Cash Collector")
        verbose_name_plural = _("Cash Collectors")
        ordering = ["-id"]

    def __str__(self):
        return f"{self.user} - {self.balance:.2f}"

    def update_frozen_status(self):
        if (
            self.balance >= settings.CASH_LIMIT
            and self.last_collected_at + timedelta(days=settings.DAYS_LIMIT)
            <= timezone.now()
        ):
            self.frozen = True
        else:
            self.frozen = False
        self.save(update_fields=["frozen"])

    def update_balance_and_collection_time(self, amount):
        # Update the collector's balance and last collection time
        self.balance += amount
        self.last_collected_at = timezone.now()
        self.save(update_fields=["last_collected_at", "balance"])

    def create_status_log(self, amount):
        from collection.models import CollectionLog

        CollectionLog.objects.create(
            collector=self, created=timezone.now(), status=self.frozen, amount=amount
        )


class Manager(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="manager",
        verbose_name=_("user"),
    )

    class Meta:
        verbose_name = _("Manager")
        verbose_name_plural = _("Managers")
        ordering = ["-id"]

    def __str__(self):
        return f"{self.user} - {self.pk}"
