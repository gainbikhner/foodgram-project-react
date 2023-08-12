from django_filters.filters import ModelMultipleChoiceFilter, NumberFilter
from django_filters.rest_framework import FilterSet

from ..recipes.models import Recipe, Tag


class RecipeFilter(FilterSet):
    """Кастомный фильтр для рецептов."""

    tags = ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all(),
    )
    is_favorited = NumberFilter(method="is_favorited_filter")
    is_in_shopping_cart = NumberFilter(method="is_in_shopping_cart_filter")

    class Meta:
        model = Recipe
        fields = ("author", "tags")

    def is_favorited_filter(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if value == 1:
                return queryset.filter(favorite__user=user)
            if value == 0:
                return queryset.exclude(favorite__user=user)
        return queryset

    def is_in_shopping_cart_filter(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if value == 1:
                return queryset.filter(shoppingcart__user=user)
            if value == 0:
                return queryset.exclude(shoppingcart__user=user)
        return queryset
