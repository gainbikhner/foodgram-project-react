from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet, ViewSet

from recipes.models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)
from users.models import Follow, User

from .filters import RecipeFilter
from .permissions import IsAuthorPatchDelete
from .serializers import (
    CustomUserSerializer,
    FavoriteSerializer,
    FollowSerializer,
    IngredientSerializer,
    RecipeCreateUpdateSerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    TagSerializer,
)


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет для тэгов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (IsAuthenticatedOrReadOnly,)


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ("^name",)


class RecipeViewSet(ModelViewSet):
    """Вьюсет для рецептов."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorPatchDelete,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        return Recipe.objects.prefetch_related(
            "ingredients_recipes__ingredient", "tags"
        ).all()

    def get_serializer_class(self):
        if self.action == "create" or "update":
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    def retrieve(self, request, pk):
        instance = get_object_or_404(Recipe, id=pk)
        serializer = RecipeSerializer(instance, context={"request": request})
        return Response(serializer.data)

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(
            page, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)


class FavoriteShoppingCartViewSet(ModelViewSet):
    """Базовый вьюсет для избранного и списка покупок."""

    queryset = None
    serializer_class = None

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def create(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        if self.queryset.filter(user=request.user, recipe=recipe).exists():
            return Response(
                {"errors": "Вы уже добавили этот рецепт."},
                status=HTTP_400_BAD_REQUEST,
            )
        data = self.queryset.create(user=request.user, recipe=recipe)
        serializer = self.get_serializer(data)
        return Response(serializer.data, status=HTTP_201_CREATED)

    def destroy(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        if self.queryset.filter(user=request.user, recipe=recipe).exists():
            self.queryset.get(user=request.user, recipe=recipe).delete()
            return Response(status=HTTP_204_NO_CONTENT)
        return Response(
            {"errors": "Вы не добавили этот рецепт."},
            status=HTTP_400_BAD_REQUEST,
        )


class FavoriteViewSet(FavoriteShoppingCartViewSet):
    """Вьюсет для избранного."""

    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer


class ShoppingCartViewSet(FavoriteShoppingCartViewSet):
    """Вьюсет для списка покупок."""

    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer

    def retrieve(self, request):
        shopping_cart = {}
        ingredients_recipes = IngredientRecipe.objects.filter(
            recipe__shoppingcart__user=request.user
        )
        for ingredient_recipe in ingredients_recipes:
            if ingredient_recipe.ingredient.name in shopping_cart.keys():
                shopping_cart[ingredient_recipe.ingredient.name][
                    1
                ] += ingredient_recipe.amount
            else:
                shopping_cart[ingredient_recipe.ingredient.name] = [
                    ingredient_recipe.ingredient.measurement_unit,
                    ingredient_recipe.amount,
                ]
        content = ""
        for ingredient, values in shopping_cart.items():
            content += f"{ingredient} ({values[0]}) — {values[1]}\n"
        return HttpResponse(content, content_type="text/plain")


class FollowViewSet(ModelViewSet):
    """Вьюсет для подписок."""

    queryset = Follow.objects.all()
    serializer_class = FollowSerializer

    def list(self, request):
        queryset = Follow.objects.filter(user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            page, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)

    def create(self, request, id):
        user = get_object_or_404(User, id=id)
        if Follow.objects.filter(user=request.user, author=user).exists():
            return Response(
                {"errors": "Вы уже подписаны на этого пользователя."},
                status=HTTP_400_BAD_REQUEST,
            )
        if request.user == user:
            return Response(
                {"errors": "Нельзя подписаться на самого себя."},
                status=HTTP_400_BAD_REQUEST,
            )
        data = Follow.objects.create(user=request.user, author=user)
        serializer = FollowSerializer(data, context={"request": request})
        return Response(serializer.data, HTTP_201_CREATED)

    def destroy(self, request, id):
        user = get_object_or_404(User, id=id)
        if Follow.objects.filter(user=request.user, author=user).exists():
            Follow.objects.get(user=request.user, author=user).delete()
            return Response(status=HTTP_204_NO_CONTENT)
        return Response(
            {"errors": "Вы не подписаны на этого пользователя."},
            status=HTTP_400_BAD_REQUEST,
        )


class UserMeViewSet(ViewSet):
    """Вьюсет для работы с текущим пользователем."""

    def retrieve(self, request):
        serializer = CustomUserSerializer(
            request.user, context={"request": request}
        )
        return Response(serializer.data)
