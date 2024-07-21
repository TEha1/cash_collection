from django.contrib import admin

from collection.models import Delivery


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ("collector", "manager", "delivered_at")
    search_fields = ("collector__user__username", "manager__user__username")
    list_filter = ("delivered_at",)
