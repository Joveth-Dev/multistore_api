from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer


class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = BaseUserCreateSerializer.Meta.fields + (
            "first_name",
            "last_name",
            "birth_date",
            "address",
        )


class CurrentUserSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = tuple(
            field for field in UserCreateSerializer.Meta.fields if field != "password"
        )
        read_only_fields = ["email"]

    def validate(self, attrs):
        """By default, each request to this serializer the user's password is
        expected and validated so we override that here for easy user update"""
        return attrs
