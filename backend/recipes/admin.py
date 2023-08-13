from django.contrib import admin

from .models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag,
    TagRecipe,
)


class TagRecipeInline(admin.TabularInline):
    model = TagRecipe
    min_num = 1
    extra = 0


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    min_num = 1
    extra = 0


class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "author")
    search_fields = ("name",)
    list_filter = ("author", "tags")
    inlines = (TagRecipeInline, IngredientRecipeInline)
    readonly_fields = ("favorite_count",)

    @admin.display(description="Колличество добавлений в избранное")
    def favorite_count(self, instance):
        return Favorite.objects.filter(recipe=instance).count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    search_fields = ("name",)
    list_filter = ("name",)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Favorite)
admin.site.register(IngredientRecipe)
admin.site.register(TagRecipe)
admin.site.register(ShoppingCart)
