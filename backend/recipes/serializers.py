import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from users.serializers import UserSerializer
from .models import (
    Ingredient,
    Recipe,
    Tag,
    IngredientRecipe,
    Favorite,
    ShoppingCart,
)
from users.models import Follow


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = IngredientRecipe
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(
        many=True, source="ingredientrecipe_set"
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, obj):
        return Favorite.objects.filter(
            user=self.context["request"].user, recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        return ShoppingCart.objects.filter(
            user=self.context["request"].user, recipe=obj
        ).exists()


class IngredientRecipeCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source="ingredient", queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientRecipe
        fields = ("id", "amount")


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = IngredientRecipeCreateSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "tags",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        recipe = super().create(validated_data)
        for ingredient_data in ingredients_data:
            IngredientRecipe(
                recipe=recipe,
                ingredient=ingredient_data["ingredient"],
                amount=ingredient_data["amount"],
            ).save()
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        recipe = super().update(instance, validated_data)
        IngredientRecipe.objects.filter(recipe=recipe).delete()
        for ingredient_data in ingredients_data:
            IngredientRecipe(
                recipe=recipe,
                ingredient=ingredient_data["ingredient"],
                amount=ingredient_data["amount"],
            ).save()
        return recipe

    def to_representation(self, instance):
        serializer = RecipeSerializer(
            instance, context={"request": self.context["request"]}
        )
        return serializer.data


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="recipe.id")
    name = serializers.ReadOnlyField(source="recipe.name")
    image = serializers.ReadOnlyField(source="recipe.image.url")
    cooking_time = serializers.ReadOnlyField(source="recipe.cooking_time")

    class Meta:
        model = Favorite
        fields = ("id", "name", "image", "cooking_time")


class ShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="recipe.id")
    name = serializers.ReadOnlyField(source="recipe.name")
    image = serializers.ReadOnlyField(source="recipe.image.url")
    cooking_time = serializers.ReadOnlyField(source="recipe.cooking_time")

    class Meta:
        model = ShoppingCart
        fields = ("id", "name", "image", "cooking_time")


class RecipeFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class FollowSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source="author.email")
    id = serializers.ReadOnlyField(source="author.id")
    username = serializers.ReadOnlyField(source="author.username")
    first_name = serializers.ReadOnlyField(source="author.first_name")
    last_name = serializers.ReadOnlyField(source="author.last_name")
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=self.context["request"].user, author=obj.author
        ).exists()

    def get_recipes(self, obj):
        return RecipeFollowSerializer(
            Recipe.objects.filter(author=obj.author), many=True
        ).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()
