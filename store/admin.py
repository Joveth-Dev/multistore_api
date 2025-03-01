from django.contrib import admin

from .models import Address, Category, Product, Store


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ["city", "province", "created_at", "updated_at"]
    list_filter = ["created_at", "updated_at"]
    search_fields = ["city", "province"]


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "name",
        "email",
        "mobile_number",
        "is_live",
        "is_open",
        "created_at",
        "updated_at",
    )
    list_filter = ["is_live", "created_at", "updated_at"]
    list_select_related = ["user", "address"]
    search_fields = ["user__email", "name", "email"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "store",
        "name",
        "created_at",
        "updated_at",
    )
    list_filter = ["created_at", "updated_at"]
    list_select_related = ["store", "store__address"]
    search_fields = ["store__email", "name"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "store",
        "price",
        "image",
        "is_available",
        "created_at",
        "updated_at",
    )
    list_filter = ["is_available", "created_at", "updated_at"]
    list_select_related = ["store__address", "category__store"]
    search_fields = ["store_email", "store__user__email", "name", "category__name"]
