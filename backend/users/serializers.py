from djoser.serializers import UserCreateSerializer, UserSerializer


class UserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = ("email", "id", "username", "first_name", "last_name")


class UserRegistrationSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )
