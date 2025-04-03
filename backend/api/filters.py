from django_filters import rest_framework as filters

from recipes.models import Recipe, Ingredient


class IngredientFilter(filters.FilterSet):
    """Фильтр для ингредиентов с возможностью поиска по имени."""
    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(filters.FilterSet):
    """Фильтр для рецептов по тегам, автору, избранному и списку покупок."""
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        label='Теги',
    )
    author = filters.NumberFilter(
        field_name='author__id',
        label='Автор',
    )
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited',
        label='В списке избранного',
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart',
        label='В списке покупок',
    )

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрация по избранному."""
        user = self.request.user
        if user.is_authenticated and value:
            return queryset.filter(favorites__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрация по списку покупок."""
        user = self.request.user
        if user.is_authenticated and value:
            return queryset.filter(shopping_carts__user=user)
        return queryset
