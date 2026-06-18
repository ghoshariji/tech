# IMS — Enterprise Inventory & Order Management System

A production-ready, full-stack Inventory & Order Management System built with **FastAPI**, **React 19**, **PostgreSQL**, and **Redis** — fully containerized with **Docker**.

---

## Features

### Core
- **Product Management** — CRUD, SKU uniqueness, low stock alerts, bulk import/export CSV
- **Customer Management** — Full customer lifecycle with soft deletes
- **Order Management** — Multi-item orders, automatic stock deduction, status workflow, cancellation with stock restore
- **Inventory Tracking** — Stock adjustments, movement history, low-stock alerts
- **Dashboard Analytics** — Real-time stats, revenue charts, recent orders

### Enterprise
- **JWT Authentication** — Access + refresh tokens with rotation
- **RBAC** — ADMIN / MANAGER / STAFF roles with enforced permissions
- **Audit Logging** — Every write action is recorded with IP, user agent, old/new values
- **Soft Deletes** — Records are never hard-deleted by default
- **Rate Limiting** — Per-endpoint via SlowAPI + Redis
- **Redis Caching** — Dashboard and product lists cached
- **Structured Logging** — JSON via Loguru, rotated log files
- **Prometheus Metrics** — `/metrics` endpoint for monitoring
- **Health Checks** — `/health` and `/readiness` endpoints

### Security
- bcrypt password hashing (cost factor 12)
- Security headers (CSP, HSTS, X-Frame-Options, etc.)
- SQL injection protection via SQLAlchemy ORM
- Input validation via Pydantic v2
- CORS strict configuration
- Trusted hosts middleware in production

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (React 19)                  │
│   Vite · Zustand · TanStack Query · Tailwind · Shadcn   │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTPS / REST API
┌───────────────────────▼─────────────────────────────────┐
│                 Backend (FastAPI)                        │
│  API Layer → Service Layer → Repository Layer → DB      │
│         JWT Auth · RBAC · Rate Limiting · Audit         │
└─────────────────┬───────────────────┬───────────────────┘
                  │                   │
         ┌────────▼──────┐   ┌────────▼──────┐
         │  PostgreSQL   │   │    Redis       │
         │  (Primary DB) │   │  (Cache/Rate)  │
         └───────────────┘   └───────────────┘
```

---

## Folder Structure

```
assess/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/   # Route handlers
│   │   ├── core/               # Exceptions, responses
│   │   ├── config/             # Settings (pydantic-settings)
│   │   ├── database/           # Engine, sessions, Redis
│   │   ├── middleware/         # Logging, security headers
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── repositories/       # Data access layer
│   │   ├── services/           # Business logic
│   │   ├── schemas/            # Pydantic v2 schemas
│   │   ├── security/           # JWT + bcrypt
│   │   ├── audit/              # Audit logging service
│   │   └── tests/              # Pytest test suites
│   ├── alembic/                # Database migrations
│   ├── Dockerfile
│   ├── render.yaml
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/              # Page components
│   │   ├── layouts/            # App layouts
│   │   ├── components/         # Reusable UI + forms
│   │   ├── services/           # API client functions
│   │   ├── store/              # Zustand state stores
│   │   ├── lib/                # Axios client, utilities
│   │   └── tests/              # Vitest test suites
│   ├── Dockerfile
│   ├── vercel.json
│   └── vite.config.ts
├── docker-compose.yml
└── .github/workflows/ci-cd.yml
```

---

## Quick Start (Docker)

```bash
# 1. Clone repository
git clone https://github.com/your-org/ims.git && cd ims

# 2. Configure environment
cp backend/.env.example backend/.env
cp .env.example .env
# Edit backend/.env — set SECRET_KEY, JWT_SECRET_KEY at minimum

# 3. Start all services
docker compose up -d --build

# 4. Run migrations
docker compose exec backend alembic upgrade head

# 5. Access the application
# Frontend: http://localhost
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs

# Default admin credentials (from .env):
# Email: admin@example.com
# Password: Admin@123456
```

---

## Local Development (Without Docker)

### Backend
```bash
cd backend

# Create virtualenv
python -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your local DB/Redis URLs

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Set VITE_API_URL=http://localhost:8000

# Start dev server
npm run dev
```

---

## Environment Variables

### Backend (`.env`)

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | ✅ | App secret (min 32 chars) |
| `JWT_SECRET_KEY` | ✅ | JWT signing key (min 32 chars) |
| `DATABASE_URL` | ✅ | Async PostgreSQL URL |
| `DATABASE_URL_SYNC` | ✅ | Sync PostgreSQL URL (Alembic) |
| `REDIS_URL` | ✅ | Redis connection URL |
| `ALLOWED_ORIGINS` | ✅ | Comma-separated CORS origins |
| `FIRST_SUPERUSER_EMAIL` | — | Admin seed email |
| `FIRST_SUPERUSER_PASSWORD` | — | Admin seed password |
| `SMTP_*` | — | Email configuration |

### Frontend (`.env`)

| Variable | Description |
|---|---|
| `VITE_API_URL` | Backend API base URL |

---

## API Documentation

| Endpoint | Description |
|---|---|
| `GET /docs` | Swagger UI (development only) |
| `GET /redoc` | ReDoc UI (development only) |
| `GET /openapi.json` | OpenAPI schema |
| `GET /health` | Liveness check |
| `GET /readiness` | Readiness check (DB + Redis) |
| `GET /metrics` | Prometheus metrics |

### API Endpoints Summary

```
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
POST   /api/v1/auth/logout
GET    /api/v1/auth/me

GET    /api/v1/products
POST   /api/v1/products
GET    /api/v1/products/{id}
PUT    /api/v1/products/{id}
DELETE /api/v1/products/{id}
GET    /api/v1/products/export/csv

GET    /api/v1/customers
POST   /api/v1/customers
GET    /api/v1/customers/{id}
PUT    /api/v1/customers/{id}
DELETE /api/v1/customers/{id}

GET    /api/v1/orders
POST   /api/v1/orders
GET    /api/v1/orders/{id}
PUT    /api/v1/orders/{id}
DELETE /api/v1/orders/{id}  (cancel)
GET    /api/v1/orders/export/csv

POST   /api/v1/inventory/adjust
GET    /api/v1/inventory/history
GET    /api/v1/inventory/low-stock

GET    /api/v1/dashboard

GET    /api/v1/audit
GET    /api/v1/users
POST   /api/v1/users
...
```

---

## Testing

### Backend
```bash
cd backend
pytest                          # Run all tests
pytest --cov=app                # With coverage
pytest app/tests/api/           # API tests only
pytest app/tests/unit/          # Unit tests only
```

### Frontend
```bash
cd frontend
npm run test                    # Run tests
npm run test:coverage           # With coverage report
```

---

## Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1

# Check current revision
alembic current
```

---

## Deployment

### Backend → Render
1. Push code to GitHub
2. Connect repository to Render
3. Set environment variables in Render dashboard
4. Set build command: `pip install -r requirements.txt && alembic upgrade head`
5. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add PostgreSQL and Redis add-ons

### Frontend → Vercel
1. Connect GitHub repo to Vercel
2. Set framework to **Vite**
3. Set `VITE_API_URL` to your Render backend URL
4. Deploy

### CI/CD (GitHub Actions)
Required secrets:
- `RENDER_API_KEY` — Render API key
- `RENDER_SERVICE_ID` — Render service ID
- `VERCEL_TOKEN` — Vercel token

---

## Security Features

| Feature | Implementation |
|---|---|
| Password hashing | bcrypt (cost 12) |
| Token auth | JWT HS256 (access + refresh) |
| Token rotation | Refresh tokens invalidated on use |
| Rate limiting | SlowAPI + Redis (100 req/min global, 5/min login) |
| SQL injection | SQLAlchemy ORM (parameterized queries) |
| XSS | CSP headers + Pydantic validation |
| CSRF | SameSite cookies + CORS origin restriction |
| Clickjacking | `X-Frame-Options: DENY` |
| Secrets | Environment variables only — never hardcoded |

---

## Troubleshooting

**DB connection error on startup**
- Ensure PostgreSQL is running and `DATABASE_URL` is correct
- Check that the database `inventory_db` exists

**Redis not connecting**
- The app degrades gracefully if Redis is unavailable
- Check `REDIS_URL` and Redis credentials

**JWT errors after restart**
- If `JWT_SECRET_KEY` changes, all existing tokens are invalidated — users must re-login

**Migrations fail**
- Ensure `DATABASE_URL_SYNC` uses `psycopg2` not `asyncpg` (Alembic requires synchronous driver)
# tech
