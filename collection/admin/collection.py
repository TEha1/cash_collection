from django.contrib import admin

from collection.models import Collection, CollectionLog


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ("task", "amount", "collected_at", "delivered")
    search_fields = ("task__title", "amount")
    list_filter = ("delivered", "collected_at")


@admin.register(CollectionLog)
class CollectionLogAdmin(admin.ModelAdmin):
    list_display = ("collector", "created", "status", "amount")
    search_fields = ("collector__user__username", "created")
    list_filter = ("status", "created")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
