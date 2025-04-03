from django.contrib import admin

from users.models import User, Subscription


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Класс для представления модели User в админ-зоне."""
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'avatar',
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

    def save_model(self, request, obj, form, change):
        """Хешируем новый пароль."""
        if 'password' in form.changed_data:
            obj.set_password(obj.password)
        obj.save()


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Класс для представления модели Subscription в админ-зоне."""
    list_display = ('author', 'user', )
    search_fields = ('user__username', 'author__username')
    list_filter = ('author',)
