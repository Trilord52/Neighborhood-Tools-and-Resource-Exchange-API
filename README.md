# Neighborhood Tools and Resource Exchange API

Backend REST API for sharing tools and resources within a neighborhood, built with Django and Django REST Framework.

## Technology stack

- Python / Django
- Django REST Framework
- SQLite for development (PostgreSQL recommended for production)

## Local setup

1. Create and activate a virtual environment (recommended).
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Apply migrations:

```bash
python manage.py migrate
```

4. Create a superuser (optional, for Django admin):

```bash
python manage.py createsuperuser
```

5. Run the development server:

```bash
python manage.py runserver
```

## Core concepts

- **Users** – authenticated community members (Django built‑in `User`).
- **Categories** – group resources (e.g. Books, Tools, Electronics).
- **Resources** – shareable items owned by a user.
- **Borrow requests** – track requests to borrow resources and their status.

## Authentication

Token based authentication using DRF's `TokenAuthentication`.

1. **Register**

`POST /api/register/`

Body:

```json
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "strongpassword123"
}
```

Response:

```json
{
  "token": "<auth_token>",
  "user": {
    "id": 1,
    "username": "alice",
    "email": "alice@example.com",
    "date_joined": "...",
    "is_active": true
  }
}
```

2. **Login**

`POST /api/login/`

Body:

```json
{
  "username": "alice",
  "password": "strongpassword123"
}
```

Response is the same shape as register, returning a token.

3. **Current user**

`GET /api/me/`

Headers:

`Authorization: Token <auth_token>`

4. **Obtain token using DRF's built-in view**

If you already have a user and just want a token (similar to the Week 3 `api_project`):

`POST /api/token/`

Body:

```json
{
  "username": "alice",
  "password": "strongpassword123"
}
```

Response:

```json
{
  "token": "<auth_token>"
}
```

## Category endpoints

- `GET /api/categories/` – list categories.
- `POST /api/categories/` – create a category (authenticated).
- `GET /api/categories/{id}/` – retrieve a category.
- `PUT/PATCH /api/categories/{id}/` – update.
- `DELETE /api/categories/{id}/` – delete.

## Resource endpoints

- `GET /api/resources/` – list resources.
  - Filters:
    - `?is_available=true|false`
    - `?category=<category_id>`
     - `?search=<text>` (search in `name` and `description`)
     - `?ordering=created_at` or `?ordering=name`
   - Pagination:
     - Uses page-number pagination: `?page=1`, `?page=2`, etc.
- `POST /api/resources/` – create a resource for the current user.
- `GET /api/resources/{id}/` – retrieve a resource.
- `PUT/PATCH /api/resources/{id}/` – update (owner only).
- `DELETE /api/resources/{id}/` – delete (owner only).

Resource fields:

- `id`
- `name`
- `description`
- `owner` (username, read‑only)
- `category` (category ID)
- `is_available`
- `created_at`

## Borrow request endpoints

- `GET /api/borrow-requests/` – list requests related to the current user (as requester or owner).
  - Filters:
    - `?role=requester` – only requests you made.
    - `?role=owner` – only requests on resources you own.
    - `?status=PENDING|APPROVED|REJECTED|RETURNED`
   - Pagination:
     - Uses page-number pagination: `?page=1`, `?page=2`, etc.
- `POST /api/borrow-requests/` – create a borrow request.
- `PUT /api/borrow-requests/{id}/approve/` – approve (resource owner only).
- `PUT /api/borrow-requests/{id}/reject/` – reject (resource owner only).
- `PUT /api/borrow-requests/{id}/return/` – mark as returned (resource owner only).

Create body:

```json
{
  "resource_id": 5
}
```

Rules:

- You cannot request your own resource.
- You can only request resources that are currently available.
- Only one approved request per resource at a time.

Returned fields:

- `id`
- `resource` (ID)
- `requester` (username)
- `status`
- `created_at`

## Running tests

```bash
python manage.py test
```

