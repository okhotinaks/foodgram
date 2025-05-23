# Generated by Django 3.2 on 2025-03-18 09:02

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20250318_1350'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(error_messages={'unique': 'Пользователь с таким именем уже существует.'}, max_length=150, unique=True, validators=[django.core.validators.RegexValidator(message='Username может содержать только латинские буквы, цифры, а также символы _.@+-.', regex='^[\\w.@+-]+\\Z')], verbose_name='Имя пользователя'),
        ),
    ]
