import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from djoser.serializers import (
    UserSerializer,
    UserCreateSerializer as BaseUserCreateSerializer
)

from recipes.models import Tag, Ingredient, Recipe, RecipeIngredient
from users.models import Subscription

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Для обработки Base64."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели тега (Tag)."""
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ингредиента (Ingredient)."""
    class Meta:
        model = Ingredient
        fields = '__all__'


class UserCreateSerializer(BaseUserCreateSerializer):
    """Сериализатор для регистрации нового пользователя."""

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 'password'
        ]


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления и удаления аватара."""
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ['avatar']


class CustomUserSerializer(UserSerializer):
    """Сериализатор для кастомной модели пользователя."""
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'avatar'
        ]

    def get_is_subscribed(self, obj):
        """Подписан ли текущий пользователь на запрашиваемого автора."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.following.filter(author=obj).exists()
        return False

    def get_avatar(self, obj):
        """Формируем ссылку на автар."""
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            else:
                return obj.avatar.url
        return None


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для упрощенного вывода рецепта."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для подписки и отписки."""

    class Meta:
        model = Subscription
        fields = ('user', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=['user', 'author']
            )
        ]

    def validate(self, data):
        if data['author'] == self.context['request'].user:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя. '
            )
        return data

    def to_representation(self, instance):
        """Переопределяем представление данных."""
        return SubscriptionSerializer(
            instance.author, context=self.context).data


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.BooleanField(default=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        ]

    def get_recipes(self, obj):
        """Список рецептов пользователя."""
        recipes_limit = self.context.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit and recipes_limit.isdigit():
            recipes = recipes[:int(recipes_limit)]
        return ShortRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        """Количество рецептов пользователя."""
        return obj.recipes.count()


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиента в рецепте."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'measurement_unit', 'amount']


class RecipeGetSerializer(serializers.ModelSerializer):
    """Сериализатор для модели рецепта(только GET-запросы)."""
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source='recipe_ingredients', many=True, read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        ]

    def get_is_favorited(self, obj):
        """Находится ли рецепт в списке избранного."""
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.favorites.filter(user=user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        """находится ли рецепт в списке покупок."""
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.shopping_carts.filter(user=user).exists()
        return False


class AddIngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиента при добавлении в рецепт."""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецепта."""
    ingredients = AddIngredientInRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time'
        ]

    def validate(self, data):
        """Общая валидация для создания и обновления рецепта."""
        if self.context['request'].method in ('POST', 'PUT', 'PATCH'):
            if 'ingredients' not in data:
                raise serializers.ValidationError({
                    'ingredients': 'Это поле обязательно.'
                })
            if 'tags' not in data:
                raise serializers.ValidationError({
                    'tags': 'Это поле обязательно.'
                })
        return data

    def validate_ingredients(self, ingredients):
        """Проверка ингредиентов на уникальность и количество."""
        if ingredients:
            id_ingredients = []
            for ingredient in ingredients:
                if ingredient['amount'] < 1:
                    raise serializers.ValidationError(
                        'Минимальное количество ингредиента - 1!'
                    )
                if ingredient['id'] in id_ingredients:
                    raise serializers.ValidationError(
                        'Ингредиенты не должны повторяться!'
                    )
                id_ingredients.append(ingredient['id'])
            return ingredients

    def validate_tags(self, tags):
        """Проверка тегов на уникальность и наличие."""
        if tags:
            if len(tags) != len(set(tags)):
                raise serializers.ValidationError(
                    'Теги не должны повторяться!'
                )
            return tags

    def add_ingredients(self, recipe, ingredients):
        """Функция добавления ингредиентов в рецепт."""
        list_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(list_ingredients)

    def create(self, validated_data):
        """Функция для создания рецепта."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.add_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        """Функция для обновления рецепта."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        super().update(instance, validated_data)

        instance.tags.set(tags)
        instance.ingredients.clear()
        self.add_ingredients(instance, ingredients)
        instance.save()

        return instance

    def to_representation(self, instance):
        """Переопределяем представление данных."""
        return RecipeGetSerializer(instance, context=self.context).data
