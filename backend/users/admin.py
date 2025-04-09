from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count

from users.models import User, Subscription


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Класс для представления модели User в админ-зоне."""
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'avatar',
        'get_subscribers_count',
        'get_recipes_count',
    )
    search_fields = ('username', 'email',)
    list_display_links = ('username',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Личная информация', {
            'fields': ('username', 'first_name', 'last_name', 'avatar')
        }),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser')
        }),
    )

    add_fieldsets = (
        (None, {'fields': ('email', 'password1', 'password2')}),
        ('Личная информация', {
            'fields': ('username', 'first_name', 'last_name')
        }),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser')
        }),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            subscribers_count=Count('followers', distinct=True),
            recipes_count=Count('recipes', distinct=True)
        )

    @admin.display(description='Кол-во подписчиков')
    def get_subscribers_count(self, obj):
        """Количество подписчиков пользователя."""
        return obj.subscribers_count

    @admin.display(description='Кол-во рецептов')
    def get_recipes_count(self, obj):
        """Количество рецептов пользователя."""
        return obj.recipes_count


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Класс для представления модели Subscription в админ-зоне."""
    list_display = ('author', 'user', )
    search_fields = ('user__username', 'author__username')
    list_filter = ('author',)
