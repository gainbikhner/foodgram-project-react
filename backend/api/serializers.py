import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.serializers import (
    ImageField,
    ModelSerializer,
    PrimaryKeyRelatedField,
    ReadOnlyField,
    SerializerMethodField,
    ValidationError,
)

from recipes.models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)
from users.models import Follow


class CustomUserSerializer(UserSerializer):
    """Сериализатор для пользователей."""

    is_subscribed = SerializerMethodField()

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
        return (
            self.context["request"].user.is_authenticated
            and Follow.objects.filter(
                user=self.context["request"].user, author=obj
            ).exists()
        )


class UserRegistrationSerializer(UserCreateSerializer):
    """Сериализатор для регистрации пользователей."""

    class Meta(UserCreateSerializer.Meta):
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )


class Base64ImageField(ImageField):
    """Кастомный тип поля для изображений."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)
        return super().to_internal_value(data)


class TagSerializer(ModelSerializer):
    """Сериализатор для тэгов."""

    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class IngredientSerializer(ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class IngredientRecipeSerializer(ModelSerializer):
    """Сериализатор для инредиентов в рецепте."""

    id = ReadOnlyField(source="ingredient.id")
    name = ReadOnlyField(source="ingredient.name")
    measurement_unit = ReadOnlyField(source="ingredient.measurement_unit")

    class Meta:
        model = IngredientRecipe
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeSerializer(ModelSerializer):
    """Сериализатор для рецептов."""

    tags = TagSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(
        source="ingredients_recipes", many=True
    )
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

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
        return (
            self.context["request"].user.is_authenticated
            and Favorite.objects.filter(
                user=self.context["request"].user, recipe=obj
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        return (
            self.context["request"].user.is_authenticated
            and ShoppingCart.objects.filter(
                user=self.context["request"].user, recipe=obj
            ).exists()
        )


class IngredientRecipeCreateSerializer(ModelSerializer):
    """Сериализатор для создания инредиентов в рецепте."""

    id = PrimaryKeyRelatedField(
        source="ingredient", queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientRecipe
        fields = ("id", "amount")


class RecipeCreateUpdateSerializer(ModelSerializer):
    """Сериализатор для создания рецепта."""

    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
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
        if "ingredients" not in self.initial_data:
            recipe = super().update(instance, validated_data)
            return recipe
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

    def validate_ingredients(self, values):
        if values == []:
            raise ValidationError("Добавьте ингредиенты.")
        ingredients = []
        for value in values:
            ingredients.append(value.get("ingredient"))
        if len(ingredients) != len(set(ingredients)):
            raise ValidationError("Повторение ингредиента.")
        return values

    def validate_tags(self, values):
        if values == []:
            raise ValidationError("Добавьте тэги.")
        if len(values) != len(set(values)):
            raise ValidationError("Повторение тэга.")
        return values


class FollowRecipeSerializer(ModelSerializer):
    """Родительский сереализатор для подписок."""

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class FavoriteShoppingCartRecipeSerializer(FollowRecipeSerializer):
    """Родительский сереализатор для избранного и списка покупок."""

    id = ReadOnlyField(source="recipe.id")
    name = ReadOnlyField(source="recipe.name")
    image = ReadOnlyField(source="recipe.image.url")
    cooking_time = ReadOnlyField(source="recipe.cooking_time")


class FavoriteSerializer(FavoriteShoppingCartRecipeSerializer):
    """Сериализатор для избранного."""

    class Meta(FavoriteShoppingCartRecipeSerializer.Meta):
        model = Favorite


class ShoppingCartSerializer(FavoriteShoppingCartRecipeSerializer):
    """Сериализатор для списка продуктов."""

    class Meta(FavoriteShoppingCartRecipeSerializer.Meta):
        model = ShoppingCart


class FollowSerializer(ModelSerializer):
    """Сериализатор для подписок."""

    email = ReadOnlyField(source="author.email")
    id = ReadOnlyField(source="author.id")
    username = ReadOnlyField(source="author.username")
    first_name = ReadOnlyField(source="author.first_name")
    last_name = ReadOnlyField(source="author.last_name")
    is_subscribed = SerializerMethodField()
    recipes = FollowRecipeSerializer(source="author.recipes", many=True)
    recipes_count = SerializerMethodField()

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

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()
