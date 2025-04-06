# Foodgram - Продуктовый помощник

## Стек технологий
`Python` `YAML` `Django` `Django REST Framework` `Djoser` `API` `Nginx` `Docker` `PostgreSQL` `Gunicorn` `Postman` `GitHub Actions(CI/CD)`

## Описание 
«Фудграм» — это сайт, на котором можно публиковать собственные рецепты, добавлять чужие рецепты в избранное, подписываться на других авторов и создавать список покупок для заданных блюд.

**Ссылка на проект:**
[foodgrram.zapto.org](https://foodgrram.zapto.org/)


## Локальный запуск с Docker

**Клонировать репозиторий**
```bash
git clone git@github.com:okhotinaks/foodgram.git
```
```bash
cd foodgram/backend/
```
**Создать виртуальное окружение**
```bash
python -m venv venv
```
```bash
source venv/bin/activate
```
**Установить зависимости из файла requirements.txt**
```bash
python3 -m pip install --upgrade pip
```
```bash
pip install -r requirements.txt
```
**Создать файл .env (в корневой директории) в соответствии с примером .env.example**
```bash
cd ..
```
```bash
touch .env
```
**Перейти в директорию с docker-compose.yml**
```bash
cd infra
```
**Запустить контейнеры**
```bash
docker compose up --build
```
**Создаем и применяем миграции**
```bash
docker compose exec backend python manage.py makemigrations
```
```bash
docker compose exec backend python manage.py migrate
```
**Сборка статики**
```bash
docker compose exec backend python manage.py collectstatic
docker compose exec backend cp -r /app/collected_static/. /backend_static/static/
``` 
**Создаем суперюзера**
```bash
docker compose exec backend python manage.py createsuperuser
```
**Импорт фикстур ингредиентов**
```bash
docker compose exec backend python manage.py import_data
```
**Проект доступен по адресу:**
http://localhost:8080/

**Спецификация к API доступна по адресу:**
http://localhost:8080/api/docs/


## Запуск проекта на удаленном сервере

**Устанавливаем Docker Compose на сервер**
```
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt install docker-compose-plugin 
```
**Создаем рабочую папку на сервере**
```bash
mkdir foodgram
```
```bash
cd foodgram
```
**Копируем на сервер файлы docker-compose.production.yml и .env(пример env.example), а также папку data для импорта фикстур ингредиентов.Пример команды копирования:**
```bash
scp -i path_to_SSH/SSH_name docker-compose.production.yml \
    username@server_ip:/home/username/foodram/docker-compose.production.yml
```
где,
- path_to_SSH — путь к файлу с SSH-ключом;
- SSH_name — имя файла с SSH-ключом (без расширения);
- username — ваше имя пользователя на сервере;
- server_ip — IP вашего сервера.

**Запускаем контейнеры**
```bash
sudo docker compose -f docker-compose.production.yml up -d 
```
**Применяем миграции**
```bash
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```
**Сборка статики**
```bash
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/ 
```
**Создаем суперюзера**
```bash
sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```
**Импорт фикстур ингредиентов**
```bash
sudo docker compose -f docker-compose.production.yml exec backend python manage.py import_data
```
**Спецификация к API доступна по адресу:**
https://foodgrram.zapto.org/api/docs/


## Автоматическое развертывание (CI/CD)
Настроен деплой на сервер через GitHub Actions.
После каждого обновления репозитория (при пуше в ветку main) будет происходить:
- Проверка кода на соответсвие стандарту PEP8(с помощью пакета flake8)
- Сборка и отправка докер-образов на Docker Hub: frontend, backend, gateway
- Разворачивание проекта на удаленном сервере
- Применение миграций, сборка статики
- Отправка сообщения в Telegram в случае успеха

**Переменные окружения.**
Для работы с GitHub Actions необходимо в репозитории создать переменные окружения c вашими данными(Settings/Secret and variables):
```
DOCKER_USERNAME    - логин Docker Hub
DOCKER_PASSWORD    - пароль от Docker Hub
HOST               - публичный IP сервера
USER               - имя пользваотеля на сервере
SSH_KEY            - закрытый SSH-ключ 
SSH_PASSPHRASE     - пароль для вашего ключа
TELEGRAM_TO        - ID своего телеграм-аккаунта
TELEGRAM_TOKEN     - токен вашего бота
```

**Автор проекта:**
Охотина Ксения Николаевна - [github.com/okhotinaks](https://github.com/okhotinaks)