# Order Processing Platform

A production-ready REST API for e-commerce order processing, built with Django and Django REST Framework.

## Tech Stack

- **Python 3.12** / **Django 5.2** / **Django REST Framework 3.15**
- **PostgreSQL** (production) / SQLite (development)
- **Celery** + **Redis** for async tasks and caching
- **SimpleJWT** for authentication
- **Docker Compose** for local orchestration

## Architecture

```
apps/
├── accounts/       # User registration, JWT auth, profile management
├── common/         # Shared models, permissions, throttles, middleware
├── orders/         # Order creation/cancellation with transactional stock management
├── notifications/  # Async email notifications via Celery
├── products/       # Product catalog with filtering, search, and caching
└── reports/        # Scheduled daily order report generation
```

Key design decisions:
- **Service layer** (`orders/services.py`) encapsulates business logic with `select_for_update` to prevent overselling
- **Domain exceptions** (`orders/exceptions.py`) decouple the service layer from REST framework
- **Signal-based cache invalidation** keeps product listings fresh after writes
- **Celery Beat** generates daily revenue reports automatically

## Quick Start

### Docker Compose (recommended)

```bash
cp .env.example .env
docker-compose up --build
```

The API is available at `http://localhost:8000/api/docs/`.

### Local Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt
cp .env.example .env

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## API Endpoints

| Endpoint | Methods | Description |
|---|---|---|
| `/api/v1/auth/register/` | POST | User registration with JWT tokens |
| `/api/v1/auth/login/` | POST | Obtain JWT token pair |
| `/api/v1/auth/token/refresh/` | POST | Refresh access token |
| `/api/v1/auth/profile/` | GET, PUT, PATCH | User profile |
| `/api/v1/auth/change-password/` | POST | Change password |
| `/api/v1/auth/logout/` | POST | Blacklist refresh token |
| `/api/v1/products/` | GET, POST | Product listing with filtering and search |
| `/api/v1/products/{slug}/` | GET, PUT, PATCH, DELETE | Product detail |
| `/api/v1/categories/` | GET, POST | Category listing |
| `/api/v1/orders/` | GET, POST | List/create orders |
| `/api/v1/orders/{order_number}/` | GET | Order detail |
| `/api/v1/orders/{order_number}/cancel/` | POST | Cancel a pending order |
| `/api/v1/reports/daily/` | GET | Daily order reports (admin only) |
| `/api/docs/` | GET | Interactive Swagger documentation |

## Running Tests

```bash
# Full suite with coverage
pytest --cov --cov-report=term-missing -v

# Without external services (Redis, PostgreSQL)
DATABASE_URL=sqlite:///db.sqlite3 CELERY_BROKER_URL=memory:// CELERY_RESULT_BACKEND=cache+memory:// REDIS_URL= pytest -v
```

## Linting

```bash
ruff check .
```
