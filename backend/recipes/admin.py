from django.contrib import admin

from .models import Ingredient, IngredientRecipe, Recipe, Tag, TagRecipe, Favorite


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
    list_filter = ("author", "name", "tags")
    inlines = (TagRecipeInline, IngredientRecipeInline)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    search_fields = ("name",)
    list_filter = ("name",)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Favorite)
