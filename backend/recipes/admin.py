from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet


from .models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag,
    TagRecipe,
)


class RecipeInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        form_count = 0
        delete_count = 0
        for form in self.forms:
            form_count += 1
            if not hasattr(form, "cleaned_data"):
                continue
            data = form.cleaned_data
            if data.get("DELETE"):
                delete_count += 1
        if form_count == delete_count:
            raise ValidationError("Необходим минимум один объект.")


class TagRecipeInline(admin.TabularInline):
    model = TagRecipe
    min_num = 1
    extra = 0
    formset = RecipeInlineFormSet


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    min_num = 1
    extra = 0
    formset = RecipeInlineFormSet


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
