from django.db import models
from django.utils.translation import gettext_lazy as _


class Collection(models.Model):
    task = models.ForeignKey(
        "collection.Task",
        on_delete=models.CASCADE,
        related_name="collections",
        verbose_name=_("task"),
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("amount"),
    )
    collected_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("collected at"),
    )
    delivered = models.BooleanField(
        default=False,
        verbose_name=_("delivered"),
    )
    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("delivered at"),
    )

    class Meta:
        verbose_name = _("Collection")
        verbose_name_plural = _("Collections")
        ordering = ["-id"]

    def __str__(self):
        return f"{self.task} - {self.amount}"


class CollectionLog(models.Model):
    collector = models.ForeignKey(
        "collection.CashCollector",
        related_name="logs",
        on_delete=models.CASCADE,
        verbose_name=_("collector"),
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("amount"),
    )
    created = models.DateTimeField(verbose_name=_("creation date"))
    status = models.BooleanField(verbose_name=_("status"))

    class Meta:
        verbose_name = _("Collection Log")
        verbose_name_plural = _("Collection Logs")
        ordering = ["-id"]

    def __str__(self):
        return f"{self.collector} - {self.created}"
