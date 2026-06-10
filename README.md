# Backend Authentication and Authorization API

A backend application built with Django REST Framework, featuring a custom authentication and authorization system.

The project implements:

* user registration;
* login and logout;
* JWT authentication;
* active session storage;
* profile retrieval and update;
* soft user deletion;
* role-based access control;
* permission checks for mock business resources;
* an admin API for viewing and modifying access rules.

## Stack

* Python
* Django
* Django REST Framework
* PyJWT
* bcrypt
* SQLite for local development
* Docker for containerized startup

## Project Structure

```text
app/
├── access_control/     # roles, business elements, access rules
├── auth_system/        # registration, login, logout, JWT middleware, sessions
├── business/           # mock business API
├── config/             # Django settings / urls
├── users/              # user model and user profile API
└── manage.py
```

## Installation and Running

Clone the project:

```bash
git clone <repository-url>
cd <project-folder>
```

Install dependencies:

```bash
uv sync
```

Apply migrations:

```bash
uv run python app/manage.py migrate
```

Create roles, business elements, and access rules:

```bash
uv run python app/manage.py seed_access
```

Run the server:

```bash
uv run python app/manage.py runserver
```

The server will be available at:

```text
http://127.0.0.1:8000/
```

## Running with Docker

The project can be run in a Docker container. In the current version, Docker is used only to run the application, while the database remains SQLite.

### Building and Starting the Container

```bash
docker compose up --build
```

After startup, the application will be available at:

```text
http://127.0.0.1:8000/
```

### Applying Migrations

Run the following command in a separate terminal:

```bash
docker compose exec web uv run python app/manage.py migrate
```

### Seeding Initial Data

```bash
docker compose exec web uv run python app/manage.py seed_access
```

### Stopping the Container

```bash
docker compose down
```

### Checking Container Status

```bash
docker compose ps
```

## Docker Files

The project includes the following files:

```text
Dockerfile
docker-compose.yml
.dockerignore
```

`Dockerfile` describes the application environment:

* uses the `python:3.12-slim` image;
* installs `uv`;
* installs dependencies from `pyproject.toml` and `uv.lock`;
* copies the project into the container;
* starts Django with the `runserver 0.0.0.0:8000` command.

`docker-compose.yml` describes the container startup:

* `web` service;
* port mapping `8000:8000`;
* mounting the current project directory as a volume;
* running the application inside the container.

SQLite is used as a local database to simplify project setup. If needed, the project can be migrated to PostgreSQL by changing the `DATABASES` configuration in Django settings.

## Authentication

The project uses custom JWT authentication.

After a successful login, the server creates a `Session` record in the database and returns a JWT access token.

The JWT contains:

* `user_id`;
* `session_id`;
* `jti`;
* `exp`.

The token is passed in the header:

```text
Authorization: Bearer <access_token>
```

Each request goes through custom middleware. The middleware:

1. extracts the token from the `Authorization` header;
2. decodes and validates the JWT;
3. checks the active session in the database;
4. checks that the user is active;
5. writes the user to `request.jwt_user`;
6. writes the current session to `request.auth_session`.

If the user is not found or the token is invalid, the endpoint itself returns `401 Unauthorized` if authorization is required.

## Registration

```http
POST /api/auth/register/
```

Example:

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

During registration, the password is hashed with `bcrypt`.

A new user is automatically assigned the `user` role if this role exists in the database.

## Login

```http
POST /api/auth/login/
```

Example:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "product_user@example.com",
    "password": "password123"
  }'
```

Response:

```json
{
  "access_token": "...",
  "token_type": "Bearer"
}
```

For convenience, the token can be saved to a variable:

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

Example:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/logout/ \
  -H "Authorization: Bearer $TOKEN"
```

During logout, the current session becomes inactive. The old JWT can no longer be used, even if the token has not expired yet.

## Getting the Current User

```http
GET /api/auth/me/
```

Example:

```bash
curl http://127.0.0.1:8000/api/auth/me/ \
  -H "Authorization: Bearer $TOKEN"
```

## User API

### Get Profile

```http
GET /api/users/me/
```

```bash
curl http://127.0.0.1:8000/api/users/me/ \
  -H "Authorization: Bearer $TOKEN"
```

### Update Profile

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

### Soft Delete User

```http
DELETE /api/users/me/
```

```bash
curl -X DELETE http://127.0.0.1:8000/api/users/me/ \
  -H "Authorization: Bearer $TOKEN"
```

Deletion is soft:

* `is_active` becomes `False`;
* `deleted_at` is filled in;
* the current session becomes inactive;
* the user can no longer log in.

## Access Model

The project implements a role-based access control model.

Main tables:

### Role

Example roles:

* `admin`;
* `manager`;
* `user`;
* `guest`.

### UserRole

A link between a user and a role.

One user can have multiple roles.

### BusinessElement

A business resource for which access can be configured.

Examples:

* `users`;
* `products`;
* `orders`;
* `shops`;
* `access_rules`.

### AccessRoleRule

An access rule for a specific role and a specific business element.

Fields:

```text
read_permission
read_all_permission
create_permission
update_permission
update_all_permission
delete_permission
delete_all_permission
```

Example:

```text
role = user
element = products
read_permission = true
read_all_permission = false
create_permission = true
```

This means that a user with the `user` role can read their own products and create products, but cannot read all products.

## Permission Logic

The project uses the `has_permission(user, element_code, action)` function.

Examples:

```python
has_permission(user, "products", "read")
has_permission(user, "products", "read_all")
has_permission(user, "products", "create")
has_permission(user, "access_rules", "update")
```

Supported actions:

```text
read
read_all
create
update
update_all
delete
delete_all
```

Regular permissions, such as `read`, `update`, and `delete`, are used to access the user's own objects.

Permissions with the `_all` suffix, such as `read_all`, `update_all`, and `delete_all`, grant access to all objects of the resource.

In the mock business API, object ownership is determined by the field:

```text
owner_id
```

## 401 and 403

The project separates authorization error logic:

### 401 Unauthorized

Returned when the user is not identified:

* no token;
* invalid token;
* inactive session;
* inactive user.

### 403 Forbidden

Returned when the user is identified but does not have the required permission.

For example:

* the user is logged in;
* but the user's role does not have `create_permission` for `products`.

## Mock Business API

Business objects are not stored in the database. They are represented by mock lists in the code.

Implemented endpoints:

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

Without a token:

```bash
curl -i http://127.0.0.1:8000/api/products/
```

Expected result:

```text
401 Unauthorized
```

With a token:

```bash
curl -i http://127.0.0.1:8000/api/products/ \
  -H "Authorization: Bearer $TOKEN"
```

Creating a product:

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

An administrator can view roles, business elements, and access rules.

Access to these endpoints is checked through `access_rules`.

### Get Roles

```http
GET /api/access/roles/
```

```bash
curl -i http://127.0.0.1:8000/api/access/roles/ \
  -H "Authorization: Bearer $TOKEN"
```

### Get Business Elements

```http
GET /api/access/elements/
```

```bash
curl -i http://127.0.0.1:8000/api/access/elements/ \
  -H "Authorization: Bearer $TOKEN"
```

### Get Access Rules

```http
GET /api/access/rules/
```

```bash
curl -i http://127.0.0.1:8000/api/access/rules/ \
  -H "Authorization: Bearer $TOKEN"
```

### Update an Access Rule

```http
PATCH /api/access/rules/<rule_id>/
```

Example:

```bash
curl -i -X PATCH http://127.0.0.1:8000/api/access/rules/1/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "create_permission": false
  }'
```

Individual fields can be updated because partial update is used.

## Assigning the Admin Role for Local Testing

For local testing, the `admin` role can be assigned to a user through the shell:

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

After that, exit the shell:

```python
exit()
```

Then get a new token through login.

The project includes a separate development command for assigning the `admin` role to one of the default users:

```bash
uv run python app/manage.py seed_add__admin
```

This command is only needed for local testing.

## Seed Data

The command:

```bash
uv run python app/manage.py seed_access
```

creates:

* roles;
* business elements;
* administrator permissions for all business elements;
* `user`, `manager`, and `guest` permissions for `products`, `orders`, and `shops`.

Default permissions:

### admin

Full access to all elements.

### manager

For `products`, `orders`, and `shops`:

* can read all objects;
* can create objects;
* can update all objects;
* can delete their own objects.

### user

For `products`, `orders`, and `shops`:

* can read their own objects;
* can create objects;
* can update their own objects;
* cannot delete objects.

### guest

For `products`, `orders`, and `shops`:

* can read their own objects;
* cannot create objects;
* cannot update objects;
* cannot delete objects.

## Main Endpoints

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

## Scenario Check

Example full scenario:

1. Run migrations.
2. Run `seed_access`.
3. Register a user.
4. Log in and get a token.
5. Check `/api/auth/me/`.
6. Check `/api/users/me/`.
7. Check `/api/products/`.
8. Assign the `admin` role to the user.
9. Get a new token.
10. Check `/api/access/rules/`.
11. Update one rule through `PATCH`.
12. Run logout.
13. Check that the old token no longer works.

## Implementation Details

* Passwords are not stored in plain text; `bcrypt` is used.
* JWT is used only to identify the session and the user.
* Having a JWT alone does not grant access: the middleware additionally checks the active session in the database.
* Logout invalidates the current session.
* User deletion is soft.
* Business objects are implemented as mock data, because the main purpose of the project is to demonstrate authentication and authorization.
* Access permissions are stored in separate tables and can be modified through the admin API.
