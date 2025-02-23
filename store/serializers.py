from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Address, Category, Product, Store


class CreateAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ["city", "province"]


class StoreSerializer(serializers.ModelSerializer):
    address = CreateAddressSerializer()
    user = serializers.StringRelatedField()

    class Meta:
        model = Store
        fields = (
            "id",
            "user",
            "name",
            "image",
            "mobile_number",
            "delivery_fee",
            "description",
            "opening_time",
            "closing_time",
            "address",
            "is_open",
            "created_at",
            "updated_at",
        )
        read_only_fields = ["user", "is_open"]

    def validate(self, attrs):
        if attrs.get("opening_time") == attrs.get("closing_time"):
            raise ValidationError(
                {"operating_hours": "Opening time and closing time cannot be the same."}
            )
        return super().validate(attrs)

    def create(self, validated_data):
        user = self.context["user"]
        validated_data["user"] = user

        address_data = validated_data.pop("address", None)
        if address_data:
            new_address = Address.objects.create(**address_data)
        validated_data["address"] = new_address
        return super().create(validated_data)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
        read_only_fields = ["store"]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        user = self.context["user"]
        store = Store.objects.get(user=user)
        if Category.objects.filter(store=store, name=attrs["name"]).exists():
            raise ValidationError(
                {"name": "A category with that name already exists for this store."}
            )
        attrs["store"] = store
        return attrs


# class ProductSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Product
#         fields = "__all__"
#         read_only_fields = ["store"]

#     def create(self, validated_data):
#         user = self.context["user"]
#         store = Store.objects.get(user=user)
#         validated_data["store"] = store
#         return super().create(validated_data)
