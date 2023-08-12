from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()

NUMBER_OF_SYMBOLS = 15


class Tag(models.Model):
    """Модель для тэгов."""

    name = models.CharField("Название", max_length=200, unique=True)
    color = ColorField("Цвет в HEX", unique=True)
    slug = models.SlugField("Уникальный слаг", unique=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name[:NUMBER_OF_SYMBOLS]


class Ingredient(models.Model):
    """Модель для ингредиентов."""

    name = models.CharField("Название", max_length=200, unique=True)
    measurement_unit = models.CharField("Единицы измерения", max_length=200)

    class Meta:
        ordering = ("name",)
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name[:NUMBER_OF_SYMBOLS]


class Recipe(models.Model):
    """Модель для рецептов."""

    tags = models.ManyToManyField(
        Tag, verbose_name="Теги", through="TagRecipe"
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        related_name="recipes",
        on_delete=models.CASCADE,
    )
    ingredients = models.ManyToManyField(
        Ingredient, verbose_name="Ингредиенты", through="IngredientRecipe"
    )
    name = models.CharField("Название", max_length=200)
    image = models.ImageField("Картинка", upload_to="recipes/")
    text = models.TextField("Описание")
    cooking_time = models.PositiveSmallIntegerField(
        "Время приготовления (в минутах)", validators=(MinValueValidator(1),)
    )

    class Meta:
        ordering = ("-id",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name[:NUMBER_OF_SYMBOLS]


class TagRecipe(models.Model):
    """Связная модель для тэгов и рецептов."""

    tag = models.ForeignKey(
        Tag,
        verbose_name="Тег",
        related_name="tags_recipes",
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт",
        related_name="tags_recipes",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Тег — Рецепт"
        verbose_name_plural = "Теги — Рецепты"
        constraints = (
            models.UniqueConstraint(
                fields=("tag", "recipe"), name="unique_tag_recipe"
            ),
        )

    def __str__(self):
        return f"{self.tag} — {self.recipe}"


class IngredientRecipe(models.Model):
    """Связная модель для ингредиентов и рецептов."""

    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name="Ингредиент",
        related_name="ingredients_recipes",
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт",
        related_name="ingredients_recipes",
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        "Количество", validators=(MinValueValidator(1),)
    )

    class Meta:
        verbose_name = "Ингредиент — Рецепт"
        verbose_name_plural = "Ингредиенты — Рецепты"
        constraints = (
            models.UniqueConstraint(
                fields=("ingredient", "recipe"),
                name="unique_ingredient_recipe",
            ),
        )

    def __str__(self):
        return f"{self.ingredient} — {self.recipe}"


class FavoriteShoppingCart(models.Model):
    """Базовая модель для избранного и списка покупок."""

    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        related_name="%(class)s",
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт",
        related_name="%(class)s",
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.user} — {self.recipe}"


class Favorite(FavoriteShoppingCart):
    """Модель для избранного."""

    class Meta(FavoriteShoppingCart.Meta):
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"
        constraints = (
            models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_favorite"
            ),
        )


class ShoppingCart(FavoriteShoppingCart):
    """Модель для списка покупок."""

    class Meta(FavoriteShoppingCart.Meta):
        verbose_name = "Список покупок"
        constraints = (
            models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_shopping_cart"
            ),
        )
