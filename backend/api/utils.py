from hashids import Hashids

hashids = Hashids(min_length=6)


def generate_short_link(request, recipe_id):
    """Генерация короткой ссылки для рецепта."""
    short_link = hashids.encode(recipe_id)
    return request.build_absolute_uri(f'/s/{short_link}/')
