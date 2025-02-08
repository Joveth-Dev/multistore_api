from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from rest_framework import serializers

from .validators import validate_age


class UserCreateSerializer(BaseUserCreateSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    birth_date = serializers.DateField(validators=[validate_age], required=True)
    address = serializers.CharField(required=True)

    class Meta(BaseUserCreateSerializer.Meta):
        fields = BaseUserCreateSerializer.Meta.fields + (
            "first_name",
            "last_name",
            "birth_date",
            "address",
        )


class UserSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = tuple(
            field for field in UserCreateSerializer.Meta.fields if field != "password"
        )
        read_only_fields = ["email"]

    def validate(self, attrs):
        """By default, each request to this serializer the user's password is
        expected and validated so we override that here for easy user update"""
        return attrs
