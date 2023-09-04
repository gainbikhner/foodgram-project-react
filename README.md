# Foodgram
Сервис для публикации рецептов.

Адрес сервера: https://newfoodgram.ddns.net/  
Почта для входа в админку: alex@gmail.com  
Пароль: Admin12345

## Автор
Константин Гайнбихнер

## Технологии
- Python 3.9
- Django 3.2
- Gunicorn 20.1.0
- Nginx 1.19.3
- Docker 24.0.5
- Djoser 2.2.0

## Установка
1. Склонируйте репозиторий.
```
git clone git@github.com:kegone/foodgram-project-react.git
```
<br>

2. Находясь в головной директории, скомпилируйте проект.
```
docker compose up -d
```
<br>

3. Выполните миграции, соберите статику и скопируйте её в /backend_static/static/.
```
docker compose exec infra-backend-1 python3 manage.py migrate
docker compose exec infra-backend-1 python3 manage.py collectstatic
docker compose exec infra-backend-1 cp -r collected_static/. ../backend_static/static/
```
<br>

Сервис доступен по 80 порту https://localhost/

## Примеры API
Регистрация пользователя
```
POST http://localhost/api/users/

{
  "email": "vpupkin@yandex.ru",
  "username": "vasya.pupkin",
  "first_name": "Вася",
  "last_name": "Пупкин",
  "password": "Qwerty123"
}
```

Создание рецепта
```
POST http://localhost/api/recipes/

{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```

## Документация API
http://localhost/api/docs/redoc.html

## Создать администратора
```
docker exec -it infra-backend-1 bash
python3 manage.py createsuperuser
```

## Импорт ингредиентов
```
cd data/
docker cp ingredients.csv foodgram-db-1:/ingredients.csv
docker exec -it foodgram-db-1 psql -U <ваш POSTGRES_USER> -d <ваш POSTGRES_DB>
COPY recipes_ingredient(name, measurement_unit) FROM '/ingredients.csv' WITH (FORMAT csv);
```

## Пример .env
```
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
POSTGRES_DB=foodgram
DB_HOST=foodgram
DB_PORT=5432
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=127.0.0.1 localhost
```
