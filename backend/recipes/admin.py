from django.contrib import admin

from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    RecipeIngredient,
    Favorite,
    ShoppingCart,
)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    autocomplete_fields = ['ingredient']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Класс для представления модели Tag в админ-зоне."""
    list_display = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_display_links = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Класс для представления модели Ingredient в админ-зоне."""
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_display_links = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Класс для представления модели Recipe в админ-зоне."""
    list_display = ('name', 'author', 'favorite_count')
    search_fields = ('name', 'author__username',)
    list_filter = ('tags',)
    filter_horizontal = ('tags', 'ingredients')
    inlines = [RecipeIngredientInline]

    @admin.display(description='В избранном')
    def favorite_count(self, obj):
        """Подсчитываем количество добавлений рецепта в избранное."""
        return Favorite.objects.filter(recipe=obj).count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Класс для представления модели Favorite в админ-зоне."""
    list_display = ('user', 'recipe')
    list_filter = ('user',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Класс для представления модели ShoppingCart в админ-зоне."""
    list_display = ('user', 'recipe')
    list_filter = ('user',)
