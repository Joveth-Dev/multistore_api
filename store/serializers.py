from django.conf import settings
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
            "email",
            "image",
            "mobile_number",
            "delivery_fee",
            "description",
            "opening_time",
            "closing_time",
            "address",
            "is_open",
            "is_live",
            "created_at",
            "updated_at",
        )
        read_only_fields = ["user", "is_open"]

    def validate(self, attrs):
        opening_time = attrs.get("opening_time")
        closing_time = attrs.get("closing_time")

        if opening_time is not None and closing_time is not None:
            if opening_time == closing_time:
                raise ValidationError(
                    {
                        "operating_hours": "Opening time and closing time cannot be the same."
                    }
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

    def update(self, instance: Store, validated_data):
        address_data = validated_data.pop("address", None)

        if address_data:
            address_instance = instance.address
            for attr, value in address_data.items():
                setattr(address_instance, attr, value)
            address_instance.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def to_representation(self, instance: Store):
        data = super().to_representation(instance)
        data["display_name"] = instance.get_display_name()
        return data


class CategorySerializer(serializers.ModelSerializer):
    store = serializers.StringRelatedField()

    class Meta:
        model = Category
        fields = "__all__"
        read_only_fields = ["store"]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        user = self.context["user"]
        store = Store.objects.get(user=user)
        if Category.objects.filter(store=store, name=attrs.get("name")).exists():
            raise ValidationError(
                {"name": "A category with that name already exists in your store"}
            )
        attrs["store"] = store
        return attrs


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class ListAndRetrieveProductSerializer(serializers.ModelSerializer):
    store = serializers.StringRelatedField()
    category = ProductCategorySerializer()

    class Meta:
        model = Product
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["image"] = f"{settings.BASE_URL}{data.get('image')}"
        return data


class ProductSerializer(serializers.ModelSerializer):
    store = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = ["store"]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        user = self.context["user"]
        store = Store.objects.get(user=user)
        product_name = attrs.get("name")
        existing_products = Product.objects.filter(store=store, name=product_name)
        if self.instance:
            existing_products = existing_products.exclude(pk=self.instance.pk)
        if existing_products.exists():
            raise ValidationError(
                {"name": "A product with that name already exists in your store"}
            )
        attrs["store"] = store
        return attrs
