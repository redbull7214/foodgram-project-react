# Проект: Foodgram - Продуктовый помощник
### Описание
Онлайн-сервис и API для него. На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

### Сервис предоставляет функционал:

- Регистрация пользователя
- Авторизация зарегистрированного пользователя
- Создание/редактирование/удаление рецепта авторизованным пользователем
- Подписка на пользователя/просмотр подписок пользователя
- Добавление рецепта в список избранных/просмотр избранных рецептов
- Добавление рецепта в список покупок
- Просмотр корзины покупок/загрузка списка покупок в виде файла .pdf

### Проект доступен по адресу:
http://51.250.88.241/
### Документация к проекту:
http://51.250.88.241/api/docs/
### Стек технологий
Python 3.8.10, Django 4.0.2, Django REST Framework 3.13.1, PostgresQL, Docker, Yandex.Cloud, Nginx, 
## _Как запустить проект:_
Клонировать репозиторий и перейти в него в командной строке:
```sh
git clone https://github.com/redbull7214/foodgram-project-react
```
Создать виртуальное окружение, обновить pip
```sh
python -m venv venv
source venv/Scripts/activate
pip install --upgrade pi
```
Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
Выполнить миграции
```
python manage.py migrate
```
# Запустить приложение в контейнерах
Перейти в папку infra и выполнить команду
```sh
docker-compose up -d
```
