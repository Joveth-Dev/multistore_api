from django.contrib import admin

from .models import Address, Category, Product, Store


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ["city", "province", "created_at", "updated_at"]


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "name",
        "email",
        "mobile_number",
        "is_open",
        "created_at",
        "updated_at",
    )
    search_fields = ["user__email", "name", "email"]
    list_select_related = ["user"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "store",
        "name",
        "created_at",
        "updated_at",
    )
    list_select_related = ["store"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "store",
        "price",
        "image",
        "created_at",
        "updated_at",
    )
    list_select_related = ["store", "category"]
