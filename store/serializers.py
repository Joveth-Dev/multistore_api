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


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
        read_only_fields = ["store"]

    def create(self, validated_data):
        user = self.context["user"]
        store = Store.objects.get(user=user)
        self.validate_user_has_store(user)
        self.validate_unique_name(store, validated_data.get("name"))
        validated_data["store"] = store
        return super().create(validated_data)

    def validate_user_has_store(self, user):
        if not Store.objects.filter(user=user).exists():
            raise ValidationError(
                {"store": "You must be a store owner to be able to create a category"}
            )

    def validate_unique_name(self, store: Store, category_name: str):
        if Category.objects.filter(store=store, name=category_name).exists():
            raise ValidationError(
                {"name": f"A category with that name already exists for {store.name}."}
            )


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
