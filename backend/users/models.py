from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.validators import UnicodeUsernameValidator

from .constants import EMAIL_MAX_LENGTH, NAME_MAX_LENGTH


class User(AbstractUser):
    """Модель для пользователя."""
    email = models.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
        verbose_name='Адрес электронной почты',
        error_messages={
            'unique': 'Такой адрес уже зарегистрирован.'
        },
    )
    username = models.CharField(
        max_length=NAME_MAX_LENGTH,
        unique=True,
        verbose_name='Имя пользователя',
        validators=[UnicodeUsernameValidator()],
        error_messages={
            'unique': 'Пользователь с таким именем уже существует.'
        },
    )
    first_name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name='Фамилия'
    )
    avatar = models.ImageField(

        null=True,
        blank=True,
        upload_to='users/',
        verbose_name='Фото пользователя'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель для подписок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Пользователь'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подпискa'
        verbose_name_plural = 'Подписки'
        ordering = ['author']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='follow_unique'
            )
        ]

    def save(self, *args, **kwargs):
        if self.user == self.author:
            raise ValidationError('Нельзя подписаться на самого себя.')
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
