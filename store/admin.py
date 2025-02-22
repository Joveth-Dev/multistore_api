from django.contrib import admin

from .models import Store


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "mobile_number",
        "delivery_fee",
        "opening_time",
        "closing_time",
        "created_at",
        "updated_at",
    )
    ordering = ["-updated_at", "-created_at"]
