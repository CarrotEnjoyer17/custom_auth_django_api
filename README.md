# Effective Mobile Test Task

Backend-приложение на Django REST Framework с кастомной системой аутентификации и авторизации.

Проект реализует:

* регистрацию пользователя;
* вход и выход из системы;
* JWT-аутентификацию;
* хранение активных сессий;
* получение и обновление профиля;
* мягкое удаление пользователя;
* ролевую модель доступа;
* проверку прав на mock business resources;
* API для администратора для просмотра и изменения правил доступа.

## Стек

* Python
* Django
* Django REST Framework
* PyJWT
* bcrypt
* SQLite для локальной разработки
* Docker для контейнерезированного запуска

## Структура проекта

```text
app/
├── access_control/     # роли, бизнес-элементы, правила доступа
├── auth_system/        # регистрация, логин, логаут, JWT middleware, sessions
├── business/           # mock business API
├── config/             # Django settings / urls
├── users/              # модель пользователя и user profile API
└── manage.py
```

## Установка и запуск

Клонировать проект:

```bash
git clone <repository-url>
cd <project-folder>
```

Установить зависимости:

```bash
uv sync
```

Применить миграции:

```bash
uv run python app/manage.py migrate
```

Создать роли, бизнес-элементы и правила доступа:

```bash
uv run python app/manage.py seed_access
```

Запустить сервер:

```bash
uv run python app/manage.py runserver
```

Сервер будет доступен по адресу:

```text
http://127.0.0.1:8000/
```


## Запуск через Docker

Проект можно запустить в Docker-контейнере. В текущей версии Docker используется только для запуска приложения, база данных остается SQLite.

### Сборка и запуск контейнера

```bash
docker compose up --build
```

После запуска приложение будет доступно по адресу:

```text
http://127.0.0.1:8000/
```

### Применение миграций

В отдельном терминале выполнить:

```bash
docker compose exec web uv run python app/manage.py migrate
```

### Заполнение тестовых данных

```bash
docker compose exec web uv run python app/manage.py seed_access
```

### Остановка контейнера

```bash
docker compose down
```

### Проверка состояния контейнеров

```bash
docker compose ps
```

## Docker-файлы

В проекте добавлены:

```text
Dockerfile
docker-compose.yml
.dockerignore
```

`Dockerfile` описывает окружение приложения:

* используется образ `python:3.12-slim`;
* устанавливается `uv`;
* зависимости устанавливаются из `pyproject.toml` и `uv.lock`;
* проект копируется внутрь контейнера;
* Django запускается командой `runserver 0.0.0.0:8000`.

`docker-compose.yml` описывает запуск контейнера:

* сервис `web`;
* проброс порта `8000:8000`;
* подключение текущей папки проекта как volume;
* запуск приложения внутри контейнера.

SQLite используется как локальная база данных для упрощения проверки тестового задания. При необходимости проект можно перевести на PostgreSQL, изменив настройки `DATABASES` в Django settings.


## Аутентификация

В проекте используется кастомная JWT-аутентификация.

После успешного логина сервер создает запись `Session` в базе данных и возвращает JWT access token.

JWT содержит:

* `user_id`;
* `session_id`;
* `jti`;
* `exp`.

Токен передается в заголовке:

```text
Authorization: Bearer <access_token>
```

Каждый запрос проходит через custom middleware. Middleware:

1. достает токен из `Authorization`;
2. декодирует и проверяет JWT;
3. проверяет активную сесию в базе;
4. проверяет, что пользователь активен;
5. записывает пользователя в `request.jwt_user`;
6. записывает текущую сессию в `request.auth_session`.

Если пользователь не найден или токен невалиден, endpoint сам возвращает `401 Unauthorized`, если для него требуется авторизация.

## Регистрация

```http
POST /api/auth/register/
```

Пример:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Product",
    "last_name": "Tester",
    "middle_name": "",
    "email": "product_user@example.com",
    "password": "password123",
    "password_repeat": "password123"
  }'
```

При регистрации пароль хешируется через `bcrypt`.

Новому пользователю автоматически назначается роль `user`, если такая роль есть в базе.

## Логин

```http
POST /api/auth/login/
```

Пример:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "product_user@example.com",
    "password": "password123"
  }'
```

Ответ:

```json
{
  "access_token": "...",
  "token_type": "Bearer"
}
```

Для удобства можно сохранить токен в переменную:

```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "product_user@example.com",
    "password": "password123"
  }' | jq -r '.access_token')
```

## Logout

```http
POST /api/auth/logout/
```

Пример:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/logout/ \
  -H "Authorization: Bearer $TOKEN"
```

При logout текущая сессич становится неактивной. Старый JWT больше не сможет использоваться, даже если срок действия токена еще не истек.

## Получение текущего пользователя

```http
GET /api/auth/me/
```

Пример:

```bash
curl http://127.0.0.1:8000/api/auth/me/ \
  -H "Authorization: Bearer $TOKEN"
```

## User API

### Получить профиль

```http
GET /api/users/me/
```

```bash
curl http://127.0.0.1:8000/api/users/me/ \
  -H "Authorization: Bearer $TOKEN"
```

### Обновить профиль

```http
PATCH /api/users/me/
```

```bash
curl -X PATCH http://127.0.0.1:8000/api/users/me/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "first_name": "UpdatedName",
    "last_name": "UpdatedLastName"
  }'
```

### Мягко удалить пользователя

```http
DELETE /api/users/me/
```

```bash
curl -X DELETE http://127.0.0.1:8000/api/users/me/ \
  -H "Authorization: Bearer $TOKEN"
```

Удаление мягкое:

* `is_active` становится `False`;
* заполняется `deleted_at`;
* текущая сессия становится неактивной;
* пользователь больше не может войти в систему.

## Модель доступа

В проекте реализована ролевая модель доступа.

Основные таблицы:

### Role

Примеры ролей:

* `admin`;
* `manager`;
* `user`;
* `guest`.

### UserRole

Связка пользователя и роли.

Один пользователь может иметь несколько ролей.

### BusinessElement

Бизнес-ресурс, к которому можно настраивать доступ.

Примеры:

* `users`;
* `products`;
* `orders`;
* `shops`;
* `access_rules`.

### AccessRoleRule

Правило доступа для конкретной роли и конкретного бизнес-элемента.

Поля:

```text
read_permission
read_all_permission
create_permission
update_permission
update_all_permission
delete_permission
delete_all_permission
```

Пример:

```text
role = user
element = products
read_permission = true
read_all_permission = false
create_permission = true
```

Это означает, что пользователь с ролью `user` может читать свои products и создавать products, но не может читать все products.

## Логика прав

В проекте используется функция `has_permission(user, element_code, action)`.

Примеры:

```python
has_permission(user, "products", "read")
has_permission(user, "products", "read_all")
has_permission(user, "products", "create")
has_permission(user, "access_rules", "update")
```

Поддерживаемые действия:

```text
read
read_all
create
update
update_all
delete
delete_all
```

Обычные permissions, например `read`, `update`, `delete`, используются для доступа к своим объектам.

Permissions с суффиксом `_all`, например `read_all`, `update_all`, `delete_all`, дают доступ ко всем объектам ресурса.

В mock business API принадлежность объекта определяется по полю:

```text
owner_id
```

## 401 и 403

В проекте разделена логика ошибок авторизации:

### 401 Unauthorized

Возвращается, если пользователь не определен:

* нет токена;
* токен невалидный;
* сессия неактивна;
* пользователь неактивен.

### 403 Forbidden

Возвращается, если пользователь определен, но у него нет нужного права.

Например:

* пользователь залогинен;
* но у его роли нет `create_permission` для `products`.

## Mock Business API

Бизнес-объекты не хранятся в базе данных. Они представлены mock-списками в коде.

Реализованы endpoints:

```http
GET  /api/products/
POST /api/products/

GET  /api/orders/
GET  /api/shops/
```

### Products

```http
GET /api/products/
```

Без токена:

```bash
curl -i http://127.0.0.1:8000/api/products/
```

Ожидаемый результа:

```text
401 Unauthorized
```

С токеном:

```bash
curl -i http://127.0.0.1:8000/api/products/ \
  -H "Authorization: Bearer $TOKEN"
```

Создание товара:

```bash
curl -i -X POST http://127.0.0.1:8000/api/products/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "New product",
    "price": 1000
  }'
```

## Admin Access API

Администратор может смотреть роли, бизнес-элементы и правила доступа.

Доступ к этим endpoints проверяется через `access_rules`.

### Получить роли

```http
GET /api/access/roles/
```

```bash
curl -i http://127.0.0.1:8000/api/access/roles/ \
  -H "Authorization: Bearer $TOKEN"
```

### Получить бизнес-элементы

```http
GET /api/access/elements/
```

```bash
curl -i http://127.0.0.1:8000/api/access/elements/ \
  -H "Authorization: Bearer $TOKEN"
```

### Получить правила доступа

```http
GET /api/access/rules/
```

```bash
curl -i http://127.0.0.1:8000/api/access/rules/ \
  -H "Authorization: Bearer $TOKEN"
```

### Изменить правило доступа

```http
PATCH /api/access/rules/<rule_id>/
```

Пример:

```bash
curl -i -X PATCH http://127.0.0.1:8000/api/access/rules/1/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "create_permission": false
  }'
```

Изменять можно отдельные поля, так как используется partial update.

## Назначение admin-роли для локального тестирования

Для локального тестирования можно назначить пользователю роль `admin` через shell:

```bash
uv run python app/manage.py shell
```

```python
from users.models import User
from access_control.models import Role, UserRole

user = User.objects.get(email="product_user@example.com")
admin_role = Role.objects.get(code="admin")

UserRole.objects.get_or_create(user=user, role=admin_role)
```

После этого нужно выйти из shell:

```python
exit()
```

И снова получить токен через login.

В проекте есть отдельная dev-команда для назначения admin-роли одному из дефолтных пользователей, ее можно запустить так:

```bash
uv run python app/manage.py seed_add__admin
```

Эта команда нужна только для локального тестирования.

## Seed data

Команда:

```bash
uv run python app/manage.py seed_access
```

создает:

* роли;
* бизнес-элементы;
* права администратора на все бизнес-элементы;
* права `user`, `manager`, `guest` на `products`, `orders`, `shops`.

Права по умолчанию:

### admin

Полный доступ ко всем элементам.

### manager

Для `products`, `orders`, `shops`:

* может читать все;
* может создавать;
* может обновлять все;
* может удалять свои объекты.

### user

Для `products`, `orders`, `shops`:

* может читать свои объекты;
* может создавать;
* может обновлять свои объекты;
* не может удалять.

### guest

Для `products`, `orders`, `shops`:

* может читать свои объекты;
* не может создавать;
* не может обновлять;
* не может удалять.

## Основные endpoint'ы

```text
POST   /api/auth/register/
POST   /api/auth/login/
POST   /api/auth/logout/
GET    /api/auth/me/

GET    /api/users/me/
PATCH  /api/users/me/
DELETE /api/users/me/

GET    /api/products/
POST   /api/products/
GET    /api/orders/
GET    /api/shops/

GET    /api/access/roles/
GET    /api/access/elements/
GET    /api/access/rules/
PATCH  /api/access/rules/<rule_id>/
```

## Проверка сценария

Пример полного сценария:

1. Запустить миграции.
2. Выполнить `seed_access`.
3. Зарегистрировать пользователя.
4. Залогиниться и получить token.
5. Проверить `/api/auth/me/`.
6. Проверить `/api/users/me/`.
7. Проверить `/api/products/`.
8. Назначить пользователю роль `admin`.
9. Получить новый token.
10. Проверить `/api/access/rules/`.
11. Изменить одно правило через `PATCH`.
12. Выполнить logout.
13. Проверить, что старый token больше не работает.

## Особенности реализации

* Пароли не хранятся в открытом виде, используется `bcrypt`.
* JWT используется только для идентификации сессии и пользователя.
* Наличие JWT само по себе не дает доступ: middleware дополнительно проверяет активную сессию в базе.
* Logout инвалидирует текущую сессию.
* Удаление пользователя мягкое.
* Бизнес-объекты сделаны mock-данными, так как основная цель проекта — показать работу authentication и authorization.
* Права доступа вынесены в отдельные таблицы и могут изменяться через admin API.

