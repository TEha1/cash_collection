from decimal import Decimal

from django.db import models
from django.db.models import Sum
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _


class Task(models.Model):
    cash_collector = models.ForeignKey(
        "collection.CashCollector",
        on_delete=models.CASCADE,
        related_name="tasks",
        verbose_name=_("cash collector"),
    )
    customer_name = models.CharField(
        max_length=255,
        verbose_name=_("customer name"),
    )
    customer_address = models.CharField(
        max_length=255,
        verbose_name=_("customer address"),
    )
    amount_due = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("amount due"),
    )
    amount_due_at = models.DateTimeField()
    collected_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("collected at"),
    )

    class Meta:
        verbose_name = _("Task")
        verbose_name_plural = _("Tasks")
        ordering = ["amount_due_at"]

    def __str__(self):
        return f"{self.customer_name} - {self.amount_due:.2f}"

    @cached_property
    def collected_amount(self) -> Decimal:
        # Calculate the total collected amount for the task
        return self.collections.aggregate(collected=Sum("amount"))["collected"]

    def update_collected_at(self):
        # Check if the total collected amount matches the amount_due
        if self.collected_amount >= self.amount_due:
            self.collected_at = timezone.now()
            self.save(update_fields=["collected_at"])
