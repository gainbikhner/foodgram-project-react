from rest_framework import filters, viewsets
from rest_framework.response import Response
from django.http import HttpResponse

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


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["^name"]


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

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
        queryset = Recipe.objects.all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = RecipeSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = RecipeSerializer(
            queryset, many=True, context={"request": request}
        )
        return Response(serializer.data)


class FavoriteViewSet(viewsets.ViewSet):
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


class ShoppingCartViewSet(viewsets.ViewSet):
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


class FollowViewSet(viewsets.ViewSet):
    def retrieve(self, request):
        instance = Follow.objects.filter(user=request.user)
        serializer = FollowSerializer(instance, context={"request": request}, many=True)
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
