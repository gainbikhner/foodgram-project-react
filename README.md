# praktikum_new_diplom
Сервис для публикации рецептов.

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

Сервис доступен по 80 порту.
```
https://localhost/
```
