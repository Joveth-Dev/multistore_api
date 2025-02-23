from rest_framework import serializers

from .models import Address, Store


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

    def create(self, validated_data):
        user = self.context["user"]
        validated_data["user"] = user
        
        address_data = validated_data.pop("address", None)
        if address_data:
            new_address = Address.objects.create(**address_data)
        validated_data["address"] = new_address
        return super().create(validated_data)
