from rest_framework import filters, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from django_filters.filters import ModelMultipleChoiceFilter, NumberFilter

from .models import (
    Ingredient,
    Recipe,
    Tag,
    Favorite,
    ShoppingCart,
    IngredientRecipe,
)
from users.models import Follow, User
from .serializers import (
    IngredientSerializer,
    RecipeSerializer,
    RecipeCreateUpdateSerializer,
    TagSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer,
    FollowSerializer
)
from users.serializers import UserSerializer
from .permissions import IsAuthor


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (IsAuthenticatedOrReadOnly,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["^name"]
    pagination_class = None
    permission_classes = (IsAuthenticatedOrReadOnly,)


class RecipeFilter(FilterSet):
    tags = ModelMultipleChoiceFilter(field_name='tags__slug', to_field_name="slug", queryset=Tag.objects.all())
    is_favorited = NumberFilter(method='is_favorited_filter')
    is_in_shopping_cart = NumberFilter(method="is_in_shopping_cart_filter")

    class Meta:
        model = Recipe
        fields = ('author', 'tags')

    def is_favorited_filter(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return queryset
        if value == 1:
            return queryset.filter(favorite__user=self.request.user)
        if value == 0:
            return queryset.exclude(favorite__user=self.request.user)
        return queryset

    def is_in_shopping_cart_filter(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return queryset
        if value == 1:
            return queryset.filter(shopping_cart__user=self.request.user)
        if value == 0:
            return queryset.exclude(shopping_cart__user=self.request.user)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthor)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        return Recipe.objects.prefetch_related(
            "ingredientrecipe_set__ingredient", "tags"
        ).all()

    def get_serializer_class(self):
        if self.action == "create" or "update":
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = Recipe.objects.get(id=self.kwargs["pk"])
        serializer = RecipeSerializer(instance, context={"request": request})
        return Response(serializer.data)

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(
            queryset, many=True, context={"request": request}
        )
        return Response(serializer.data)


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def create(self, request, id):
        data = Favorite.objects.create(
            user=request.user, recipe=Recipe.objects.get(id=id)
        )
        serializer = FavoriteSerializer(data)
        return Response(serializer.data)

    def destroy(self, request, id):
        Favorite.objects.get(
            user=request.user, recipe=Recipe.objects.get(id=id)
        ).delete()
        return Response()


class ShoppingCartViewSet(viewsets.ModelViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer

    def get_queryset(self):
        return ShoppingCart.objects.filter(user=self.request.user)

    def retrieve(self, request):
        shopping_cart = {}
        ingredients_recipes = IngredientRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
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

    def create(self, request, id):
        data = ShoppingCart.objects.create(
            user=request.user, recipe=Recipe.objects.get(id=id)
        )
        serializer = ShoppingCartSerializer(data)
        return Response(serializer.data)

    def destroy(self, request, id):
        ShoppingCart.objects.get(
            user=request.user, recipe=Recipe.objects.get(id=id)
        ).delete()
        return Response()


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer

    def list(self, request):
        queryset = Follow.objects.filter(user=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = FollowSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = FollowSerializer(
            queryset, many=True, context={"request": request}
        )
        return Response(serializer.data)

    def create(self, request, id):
        data = Follow.objects.create(
            user=request.user, author=User.objects.get(id=id)
        )
        serializer = FollowSerializer(data, context={"request": request})
        return Response(serializer.data)

    def destroy(self, request, id):
        Follow.objects.get(
            user=request.user, author=User.objects.get(id=id)
        ).delete()
        return Response()


class UserMeViewSet(viewsets.ViewSet):
    """Вью-функция для работы с текущим пользователем."""

    def retrieve(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(serializer.data)
