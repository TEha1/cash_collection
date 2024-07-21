from django.contrib import admin

from collection.models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "customer_name",
        "cash_collector",
        "amount_due",
        "amount_due_at",
        "collected_at",
        "collected_amount",
    )
    search_fields = ("customer_address", "customer_name")
    readonly_fields = ("collected_at",)
    list_editable = ("cash_collector", "amount_due_at", "amount_due")
    autocomplete_fields = ("cash_collector",)
