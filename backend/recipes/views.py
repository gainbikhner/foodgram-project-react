from rest_framework import filters, viewsets
from rest_framework.response import Response

from .models import Ingredient, Recipe, Tag, Favorite
from .serializers import (
    IngredientSerializer,
    RecipeSerializer,
    RecipeCreateUpdateSerializer,
    TagSerializer,
    FavoriteSerializer,
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
