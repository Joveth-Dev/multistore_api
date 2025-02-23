from django.contrib import admin

from .models import Address, Store


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ["city", "province", "created_at", "updated_at"]


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "name",
        "mobile_number",
        "delivery_fee",
        "opening_time",
        "closing_time",
        "created_at",
        "updated_at",
        "is_open",
    )
    list_select_related = ["user"]
