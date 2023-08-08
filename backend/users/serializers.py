from djoser.serializers import UserCreateSerializer, UserSerializer
from .models import Follow
from rest_framework import serializers


class UserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        if self.context['request'].user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=self.context["request"].user, author=obj
        ).exists()


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
