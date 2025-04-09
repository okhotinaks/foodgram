from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Sum, Count
from django.http import HttpResponse
from rest_framework import viewsets, views
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from hashids import Hashids

from recipes.models import (Tag, Ingredient, RecipeIngredient,
                            Recipe, Favorite, ShoppingCart)
from api.utils import generate_short_link
from api.permissions import IsAuthorOrAdminOrReadOnly
from api.paginations import CustomPageNumberPagination
from api.filters import RecipeFilter, IngredientFilter
from .serializers import (TagSerializer,
                          IngredientSerializer,
                          CustomUserSerializer,
                          UserCreateSerializer,
                          AvatarSerializer,
                          SubscribeSerializer,
                          RecipeGetSerializer,
                          RecipeSerializer,
                          ShortRecipeSerializer)

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для упарвления пользователями."""
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPageNumberPagination

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return CustomUserSerializer

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='me'
    )
    def me(self, request):
        """Профиль текущего пользователя."""
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[IsAuthenticated],
        url_path='set_password'
    )
    def set_password(self, request):
        """Изменение пароля."""
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        if not user.check_password(current_password):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['put', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar'
    )
    def avatar(self, request):
        """Обновление или удаление аватара пользователя."""
        user = request.user

        if request.method == 'PUT':
            serializer = AvatarSerializer(user, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'DELETE':
            user.avatar.delete(save=True)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        pagination_class=CustomPageNumberPagination,
        url_path='subscriptions'
    )
    def subscriptions(self, request):
        """Подписки текущего пользователя."""
        recipes_limit = request.query_params.get('recipes_limit')
        subscriptions = request.user.following.all()
        page = self.paginate_queryset(subscriptions)
        context = {'request': request, 'recipes_limit': recipes_limit}

        if page is None:
            serializer = SubscribeSerializer(
                subscriptions, many=True, context=context
            )
            return Response(serializer.data)

        else:
            serializer = SubscribeSerializer(page, many=True, context=context)
            return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='subscribe'
    )
    def subscribe(self, request, pk=None):
        """Подписка и отписка на пользователя."""
        user = request.user
        author = get_object_or_404(User, pk=pk)

        if request.method == 'POST':
            recipes_limit = request.query_params.get('recipes_limit')
            data = {'user': user.id, 'author': author.id}
            serializer = SubscribeSerializer(
                data=data,
                context={'request': request, 'recipes_limit': recipes_limit}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            deleted_count = request.user.following.filter(
                author=author).delete()[0]
            if deleted_count > 0:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeGetSerializer
    permission_classes = [IsAuthorOrAdminOrReadOnly]
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def get_serializer_class(self):
        """Выбираем сериализатор в зависимости от запроса."""
        if self.action == ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipeSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='favorite'
    )
    def favorite(self, request, pk=None):
        """Добавление и удаление рецепта из избранного."""
        return self.general_function(request, pk, Favorite)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='shopping_cart'
    )
    def shopping_cart(self, request, pk=None):
        """Добавление и удаление рецепта из списка покупок."""
        return self.general_function(request, pk, ShoppingCart)

    def general_function(self, request, pk, model):
        """Общий метод для избранного и списка покупок."""
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            if model.objects.filter(user=user, recipe=recipe).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            model.objects.create(user=user, recipe=recipe)
            serializers = ShortRecipeSerializer(
                recipe,
                context={'request': request}
            )
            return Response(serializers.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            deleted_count = model.objects.filter(
                user=user, recipe=recipe).delete()[0]
            if deleted_count > 0:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        """Скачивание списка покупок."""
        user = request.user
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_carts__user=user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        )
        shopping_cart = 'Список покупок:\n\n'

        for ingredient in ingredients:
            shopping_cart += (
                f"{ingredient['ingredient__name']} "
                f"({ingredient['ingredient__measurement_unit']}) - "
                f"{ingredient['total_amount']}\n"
            )

        response = HttpResponse(
            shopping_cart,
            content_type='text/plain; charset=utf-8'
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.txt"'
        )
        return response

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link'
    )
    def get_short_link(self, request, pk=None):
        """Получаем короткую ссылку на рецепт."""
        recipe = get_object_or_404(Recipe, pk=pk)
        short_link = generate_short_link(request, recipe.pk)
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)


hashids = Hashids(min_length=6)


class ShortLinkView(views.APIView):
    """Редирект пользователя с короткой ссылки рецепта на полную."""

    def get(self, request, hash_result):
        recipe_id = hashids.decode(hash_result)[0]
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        return redirect(f'/recipes/{recipe.pk}/')
