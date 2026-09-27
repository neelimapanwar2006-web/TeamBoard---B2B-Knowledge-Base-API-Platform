# TeamBoard API

A Django REST Framework backend for a B2B AI-powered Knowledge Base.

## Features

- Company registration with automatic API-key generation
- JWT authentication using SimpleJWT
- Knowledge-base search across question and answer fields
- Atomic query logging
- Admin-only usage dashboard
- PostgreSQL database running in Docker
- Seed command for sample KB entries
- Automated Django API tests
- Postman collection covering 11 required scenarios

## Project structure

```text
teamboard/
├── api/
│   ├── management/commands/seed_kb.py
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── permissions.py
│   ├── signals.py
│   ├── tests.py
│   └── views.py
├── teamboard/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── postman/
│   └── TeamBoard.postman_collection.json
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── manage.py
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.12+
- Docker Desktop / Docker Engine
- Postman (for API verification)

## 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd teamboard
```

## 2. Configure environment variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Update the values in `.env`, especially `DJANGO_SECRET_KEY` and `POSTGRES_PASSWORD`.

Do not commit `.env`.

## 3. Start PostgreSQL and Django

```bash
docker compose up --build
```

The API will be available at:

```text
http://localhost:8000/
```

The PostgreSQL service is exposed on port `5432`.

## 4. Seed the knowledge base

Open another terminal:

```bash
docker compose exec web python manage.py seed_kb
```

This creates sample knowledge-base entries across the required categories.

## 5. Run tests

```bash
docker compose exec web python manage.py test
```

The test suite covers:

1. Registration creates Company and API key
2. Duplicate username
3. Successful login
4. Invalid login
5. Protected query without token
6. Successful KB query and QueryLog
7. Blank query validation
8. Zero-result query is still logged
9. CLIENT cannot access admin endpoint
10. ADMIN can access usage summary
11. QueryLog is associated with the authenticated company

## API endpoints

### Register

`POST /api/auth/register/`

Example:

```json
{
  "username": "acmecorp",
  "password": "securepass123",
  "company_name": "Acme Corp",
  "email": "dev@acmecorp.com"
}
```

Returns HTTP `201` with:

- username
- company_name
- api_key
- JWT access token

### Login

`POST /api/auth/login/`

Example:

```json
{
  "username": "acmecorp",
  "password": "securepass123"
}
```

Returns HTTP `200` with:

- access
- company_name
- api_key

### Knowledge-base query

`POST /api/kb/query/`

Header:

```text
Authorization: Bearer <access_token>
```

Body:

```json
{
  "search": "select_related"
}
```

The search is case-insensitive and checks both `question` and `answer`.

Every valid query is logged, including queries with zero matching results.

### Usage summary

`GET /api/admin/usage-summary/`

Header:

```text
Authorization: Bearer <admin_access_token>
```

Returns:

- total_queries
- active_companies
- top_search_terms

Only a Company with role `admin` can access it.

## Making a user an admin for demonstration

The assignment explicitly requires checking the Company role rather than Django's `is_staff` or `is_superuser`.

For a local demo, use Django shell:

```bash
docker compose exec web python manage.py shell
```

Then:

```python
from django.contrib.auth.models import User
from api.models import Company

user = User.objects.get(username="adminuser")
user.company.role = Company.Role.ADMIN
user.company.save(update_fields=["role"])
```

Log in again and use the new access token for:

```text
GET /api/admin/usage-summary/
```

## Postman

Import:

```text
postman/TeamBoard.postman_collection.json
```

The collection uses:

```text
base_url = http://localhost:8000
```

It contains 11 requests covering successful and failure scenarios. The registration and login requests use Postman test scripts to store tokens automatically.

## Database

PostgreSQL is the only application database. Credentials are read from environment variables and are not hardcoded in Django settings.

## Security notes

- API keys are generated server-side with `secrets.token_urlsafe(32)`.
- Company identity for KB queries comes from the authenticated JWT user, never from the request body.
- Public authentication endpoints explicitly disable the global JWT requirement.
- Admin access checks the TeamBoard Company role.
- `.env` is ignored by Git.

## Submission checklist

Before submitting the GitHub URL:

- [ ] `docker compose up --build` works
- [ ] PostgreSQL starts successfully
- [ ] migrations apply successfully
- [ ] `python manage.py seed_kb` succeeds
- [ ] `python manage.py test` passes
- [ ] Postman collection imports successfully
- [ ] All 11 Postman scenarios pass
- [ ] `.env` is not committed
- [ ] `.env.example` is committed
- [ ] `requirements.txt` has pinned versions
- [ ] README explains setup, migrations, database, seeding, tests and API usage
