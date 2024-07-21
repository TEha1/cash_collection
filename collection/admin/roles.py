from django.contrib import admin

from collection.models import CashCollector, Manager


@admin.register(CashCollector)
class CashCollectorAdmin(admin.ModelAdmin):
    list_display = ("user", "balance", "frozen", "last_collected_at")
    search_fields = ("user__username", "balance")
    list_filter = ("frozen",)


@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    list_display = ("user",)
    search_fields = ("user__username",)
