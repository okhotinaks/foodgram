from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from .constants import (TAG_MAX_LENGTH, INGREDIENT_MAX_LENGTH,
                        UNIT_LENGTH, RECIPE_MAX_LENGTH, MIN_VALUE,
                        SLUG_REGEX, SLUG_ERROR_MESSAGE)

User = get_user_model()


class Tag(models.Model):
    """Модель для тега."""
    name = models.CharField(
        max_length=TAG_MAX_LENGTH,
        unique=True,
        verbose_name='Название тега'
    )
    slug = models.SlugField(
        max_length=TAG_MAX_LENGTH,
        unique=True,
        allow_unicode=False,
        validators=[RegexValidator(
            regex=SLUG_REGEX,
            message=SLUG_ERROR_MESSAGE)
        ],
        verbose_name='Slug'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель для ингредиента."""
    name = models.CharField(
        max_length=INGREDIENT_MAX_LENGTH,
        unique=True,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=UNIT_LENGTH,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='ingredient_unique'
            )
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель для рецепта."""
    name = models.CharField(
        max_length=RECIPE_MAX_LENGTH,
        verbose_name='Название рецепта'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    text = models.TextField(verbose_name='Описание рецепта')
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Изображение'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления(мин)',
        validators=[MinValueValidator(MIN_VALUE, 'Минимальное значение - 1')]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Промежуточная модель для связи рецепт - ингредиент."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipes',
        verbose_name='Ингредиент в рецепте'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество игредиента',
        validators=[MinValueValidator(MIN_VALUE, 'Минимальное количество - 1')]
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='ingredient_in_recipe_unique'
            )
        ]

    def __str__(self):
        return f'{self.ingredient.name} - {self.amount}'


class Favorite(models.Model):
    """Модель для избранного."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='favorite_unique'
            )
        ]

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class ShoppingCart(models.Model):
    """Модель для списка покупок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_carts',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_carts',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='shopping_cart_unique'
            )
        ]

    def __str__(self):
        return f'{self.user} - {self.recipe}'
