import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """Команда для импорта ингредиентов в БД."""

    help = 'Загружает ингредиенты в базу данных'

    def handle(self, *args, **options):
        file_path = Path('/app/data') / 'ingredients.csv'
        with open(file_path, encoding='utf-8') as file:
            reader = csv.reader(file)
            for name, unit in reader:
                Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=unit)

        self.stdout.write(self.style.SUCCESS('Данные загружены успешно!'))
