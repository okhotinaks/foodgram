from rest_framework.views import APIView
from django.shortcuts import get_object_or_404, redirect

from hashids import Hashids

from recipes.models import Recipe

hashids = Hashids(min_length=6)


class ShortLinkView(APIView):
    """Редирект пользователя с короткой ссылки рецепта на полную."""

    def get(self, request, hash_result):
        recipe_id = hashids.decode(hash_result)[0]
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        return redirect(f'/recipes/{recipe.pk}/')
