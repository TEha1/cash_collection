from django.db import models
from django.utils.translation import gettext_lazy as _


class Delivery(models.Model):
    collector = models.ForeignKey(
        "collection.CashCollector",
        related_name="deliveries",
        on_delete=models.CASCADE,
        verbose_name=_("collector"),
    )
    manager = models.ForeignKey(
        "collection.Manager",
        related_name="deliveries_received",
        on_delete=models.CASCADE,
        verbose_name=_("manager"),
    )
    delivered_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("delivered at"),
    )
    collections = models.ManyToManyField(
        "collection.Collection",
        blank=True,
        verbose_name=_("collections"),
    )

    class Meta:
        verbose_name = _("Delivery")
        verbose_name_plural = _("Deliveries")
        ordering = ["-delivered_at"]

    def __str__(self):
        return f"{self.collector} - {self.delivered_at}"
