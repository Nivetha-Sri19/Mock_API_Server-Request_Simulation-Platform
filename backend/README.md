# API Mock Server & Request Simulation Platform

A FastAPI platform for creating configurable mock APIs with request validation, response scenarios, delays, API versions, permissions, request history, caching, and a dashboard.

## Stack

- Python 3.12
- FastAPI
- SQLAlchemy 2.x
- MySQL 8
- Alembic
- Redis
- JWT authentication
- pytest

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` from `.env.example`, create the MySQL database, then run:

```bash
alembic upgrade head
uvicorn app.main:app --reload
```

API documentation:

- `/docs`
- `/redoc`

## Dynamic mock APIs

Dynamic endpoints are exposed below:

```text
/mock/{configured-path}
```

The application uses a catch-all route and resolves the configured HTTP method and path against the database, so new mock APIs do not require application restart or route registration.

Example:

```text
GET /mock/users
GET /mock/products/10
POST /mock/orders
```

Path parameters use FastAPI-style syntax when the mock API is created:

```text
/products/{id}
```

## Response scenarios

Supported scenarios:

- success
- validation_error
- unauthorized
- not_found
- server_error
- custom

Select a scenario with:

```text
?__scenario=not_found
```

If the requested scenario is not configured, the success scenario is used as a fallback.

## Request validation

A version can define:

- query parameters
- path parameters
- headers
- JSON body schema

Requests are validated before the configured response is returned.

## Authentication

Management APIs require a bearer access token.

Private dynamic APIs require authentication and the `execute` permission unless the caller is the owner or an administrator.

## Database migrations

Generate a migration after model changes:

```bash
alembic revision --autogenerate -m "migration message"
```

Apply migrations:

```bash
alembic upgrade head
```

Check for model/schema differences:

```bash
alembic check
```

## Docker

```bash
docker compose up --build
```

The API is available at:

```text
http://localhost:8000
```

## Tests

```bash
pytest -q
```
