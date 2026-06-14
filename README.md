# Expense Tracker

A personal finance web application for recording income and expenses, organizing transactions by category, and managing your financial data in one place. Built with **FastAPI**, **PostgreSQL**, and server-rendered **Jinja2** templates with a layered backend architecture.

> **Note:** This project is actively being migrated from a legacy Flask prototype (`backend/`). The FastAPI application in `app/` is the current, supported codebase.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Current Features](#current-features)
- [Architecture Overview](#architecture-overview)
- [Tech Stack](#tech-stack)
- [Folder Structure](#folder-structure)
- [Database Schema](#database-schema)
- [Authentication Flow](#authentication-flow)
- [API Endpoints Currently Available](#api-endpoints-currently-available)
- [Setup Instructions](#setup-instructions)
- [Environment Variables](#environment-variables)
- [Running Migrations](#running-migrations)
- [Running Tests](#running-tests)
- [Screenshots](#screenshots)
- [Current Project Status](#current-project-status)
- [Planned Features](#planned-features)
- [License](#license)

---

## Project Overview

Expense Tracker helps users log financial transactions, classify them under income or expense categories, and review their activity through a browser-based interface. Each user owns an isolated set of categories and transactions stored in PostgreSQL.

The application exposes:

- **Server-rendered HTML pages** for login, signup, transaction entry, category settings, and navigation shells.
- **JSON REST APIs** under `/api/v1` for categories and transactions, consumed by the frontend JavaScript and suitable for future clients.

On registration, every user automatically receives a set of default categories. A demo account is seeded on application startup for local development and testing.

---

## Current Features

### Authentication & sessions

- User registration with email, password, and confirmation validation
- Login and logout with server-side session cookies
- Protected routes for authenticated users; unauthenticated HTML requests redirect to `/login`
- Password hashing with **bcrypt** via Passlib
- Demo account: `test@example.com` / `1234`

### Categories

- Full CRUD via REST API (`/api/v1/categories`)
- Settings page UI: list, create, edit, and delete categories
- Duplicate category name prevention per user
- Categories cannot be deleted while transactions still reference them
- Default categories seeded on signup:
  - **Expense:** Food, Transport, Shopping, Bills, Health
  - **Income:** Salary, Freelance, Investment

### Transactions

- Full CRUD via REST API (`/api/v1/transactions`)
- Add Expense page UI: create, list, edit, delete transactions
- Pagination and filtering by category type (`income` / `expense` / all)
- Validation: positive amounts, valid user-owned categories, no future-dated transactions
- Transaction type is derived from the linked category (not stored separately on the transaction)

### Pages & navigation

| Route | Status |
|-------|--------|
| `/login`, `/signup`, `/logout` | Fully functional |
| `/expense` | Fully functional (transaction form + table) |
| `/settings` | Fully functional (category management) |
| `/dashboard` | Protected placeholder (stat cards show `—`) |
| `/reports` | Protected placeholder |

### Infrastructure

- PostgreSQL persistence with SQLAlchemy 2.0 ORM
- Alembic database migrations
- Application health check at `/health`
- Interactive API docs at `/docs` (Swagger UI) and `/redoc`
- **48 automated tests** (unit + integration)

---

## Architecture Overview

The application follows a **layered architecture** with clear separation of concerns:

```
HTTP Request
     │
     ▼
┌─────────────┐
│   Routers   │  Route definitions, request/response mapping, auth dependencies
└──────┬──────┘
       ▼
┌─────────────┐
│  Services   │  Business rules, validation, ownership checks
└──────┬──────┘
       ▼
┌─────────────┐
│Repositories │  SQLAlchemy queries and persistence
└──────┬──────┘
       ▼
┌─────────────┐
│   Models    │  ORM entities (User, Category, Transaction, …)
└─────────────┘
```

**Supporting layers:**

- **Schemas** — Pydantic models for API request/response validation
- **Templates + Static JS** — Jinja2 HTML and vanilla JavaScript calling the REST API
- **Core** — Configuration, security, logging, shared dependencies, custom exceptions

```mermaid
flowchart LR
    Browser -->|HTML forms / fetch| Routers
    Routers --> Services
    Services --> Repositories
    Repositories --> PostgreSQL
    Routers --> Templates
    Templates --> Browser
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.8+ |
| Web framework | FastAPI |
| ASGI server | Uvicorn |
| Templates | Jinja2 |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| Database | PostgreSQL 14+ (SQLite in-memory for tests) |
| Validation | Pydantic v2 |
| Authentication | Starlette SessionMiddleware + bcrypt (Passlib) |
| Frontend | Vanilla JavaScript, custom CSS |
| Testing | pytest, httpx, FastAPI TestClient |
| Containerization | Docker Compose (PostgreSQL only) |

---

## Folder Structure

```
Expense Tracker/
├── app/
│   ├── core/                 # Config, security, dependencies, exceptions, logging
│   ├── db/                   # Database session, seed data, default categories
│   ├── models/               # SQLAlchemy ORM models
│   ├── repositories/         # Data access layer
│   ├── routers/              # FastAPI route modules
│   ├── schemas/              # Pydantic request/response schemas
│   ├── services/             # Business logic layer
│   ├── static/
│   │   ├── css/              # Application styles
│   │   └── js/               # Page scripts (expense-form, settings, utils)
│   ├── templates/
│   │   ├── auth/             # Login and signup pages
│   │   ├── components/       # Sidebar, header, toast, stat card
│   │   ├── dashboard/        # Dashboard placeholder
│   │   ├── reports/          # Reports placeholder
│   │   ├── settings/         # Category management UI
│   │   └── transactions/     # Add Expense / transaction table UI
│   └── main.py               # Application entry point
├── alembic/
│   └── versions/             # Database migration scripts
├── backend/                  # Legacy Flask app (reference only)
├── tests/
│   ├── integration/          # Auth, categories, transactions, health, DB tests
│   └── unit/                 # Auth service and security unit tests
├── .env.example              # Environment variable template
├── alembic.ini               # Alembic configuration
├── docker-compose.yml        # PostgreSQL service for local development
├── requirements.txt          # Production dependencies
└── requirements-dev.txt      # Development and test dependencies
```

---

## Database Schema

Migration: `001_initial_schema`

### Entity relationships

```mermaid
erDiagram
    users ||--o| user_profiles : has
    users ||--o{ categories : owns
    users ||--o{ transactions : owns
    categories ||--o{ transactions : classifies

    users {
        int id PK
        string email UK
        string password_hash
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    user_profiles {
        int id PK
        int user_id FK UK
        decimal monthly_salary
        string currency
        datetime created_at
    }

    categories {
        int id PK
        string name
        enum type
        int user_id FK
    }

    transactions {
        int id PK
        decimal amount
        text description
        date transaction_date
        int category_id FK
        int user_id FK
        datetime created_at
    }
```

### Tables

| Table | Description |
|-------|-------------|
| `users` | Account credentials and active status |
| `user_profiles` | Extended profile data (currency, optional monthly salary) — **schema only, no UI yet** |
| `categories` | User-owned income/expense categories; unique `(user_id, name)` |
| `transactions` | Financial entries linked to a category and user |

### Design notes

- Category type (`income` / `expense`) lives on **`categories.type`**, not on `transactions`.
- Deleting a category is **RESTRICT**ed when transactions reference it.
- Deleting a user **CASCADE**s profiles, categories, and transactions.

---

## Authentication Flow

1. **Registration** — User submits email and password on `/signup`. Passwords are hashed with bcrypt and stored in PostgreSQL. Default categories are created automatically. User is redirected to `/login`.

2. **Login** — User submits credentials on `/login`. The auth service verifies the email and bcrypt hash. On success, the user's email is stored in the server-side session (`session["user_id"]`) and a signed cookie is set.

3. **Protected access**
   - **HTML routes** use `require_login` → unauthenticated users receive a `303` redirect to `/login`.
   - **API routes** use `get_current_user` → unauthenticated requests receive `401 Unauthorized`.

4. **Logout** — Session is cleared via `POST /logout` or `GET /logout` (sidebar link). User is redirected to `/login`.

5. **Session configuration** — Cookie name, max age, and secret key are configured via environment variables (see below).

---

## API Endpoints Currently Available

### System

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | No | Application health check |

### Authentication

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET/POST | `/login` | No | Login page / authenticate |
| GET/POST | `/signup` | No | Signup page / register |
| POST | `/logout` | No | Clear session |
| GET | `/logout` | No | Clear session (sidebar) |
| GET | `/auth/status` | Optional | JSON auth status |

### Pages (HTML)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | Optional | Redirect to dashboard or login |
| GET | `/dashboard` | Yes | Dashboard placeholder |
| GET | `/expense` | Yes | Transaction form and table |
| GET | `/reports` | Yes | Reports placeholder |
| GET | `/settings` | Yes | Category management |

### Categories (`/api/v1/categories`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/categories` | Yes | List all categories |
| POST | `/api/v1/categories` | Yes | Create category |
| PUT | `/api/v1/categories/{id}` | Yes | Update category |
| DELETE | `/api/v1/categories/{id}` | Yes | Delete category |

**Create body example:**

```json
{
  "name": "Groceries",
  "type": "expense"
}
```

### Transactions (`/api/v1/transactions`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/transactions` | Yes | List transactions (paginated) |
| POST | `/api/v1/transactions` | Yes | Create transaction |
| GET | `/api/v1/transactions/{id}` | Yes | Get single transaction |
| PUT | `/api/v1/transactions/{id}` | Yes | Update transaction |
| DELETE | `/api/v1/transactions/{id}` | Yes | Delete transaction |

**Query parameters (list):**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `page` | `1` | Page number |
| `per_page` | `10` | Items per page (max 100) |
| `type` | — | Filter: `income`, `expense`, or omit for all |

**Create body example:**

```json
{
  "amount": "42.50",
  "description": "Weekly groceries",
  "transaction_date": "2026-06-10",
  "category_id": 1
}
```

### Users, Dashboard, Reports (stubs)

These authenticated endpoints confirm router wiring but do **not** return business data yet:

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/users/me` | Current user profile |
| GET | `/api/v1/users/status` | Stub status response |
| GET | `/api/v1/dashboard/status` | Stub status response |
| GET | `/api/v1/reports/status` | Stub status response |

---

## Setup Instructions

### Prerequisites

- Python 3.8+
- pip
- PostgreSQL 14+ **or** Docker

### 1. Clone and create a virtual environment

```bash
git clone <repository-url>
cd "Expense Tracker"

python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 3. Configure environment

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Edit `.env` and set at minimum `DATABASE_URL` and `SECRET_KEY`.

### 4. Start PostgreSQL

**Option A — Docker (recommended)**

```bash
docker compose up -d
```

| Setting | Value |
|---------|-------|
| Host | `localhost` |
| Port | `5432` |
| User | `postgres` |
| Password | `postgres` |
| Database | `expense_tracker` |

**Option B — Local PostgreSQL**

Create the database manually:

```sql
CREATE DATABASE expense_tracker;
```

Update `DATABASE_URL` in `.env` to match your credentials.

### 5. Run migrations

```bash
alembic upgrade head
```

### 6. Start the application

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open [http://127.0.0.1:8000/login](http://127.0.0.1:8000/login) and sign in with the demo account or register a new user.

---

## Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | `Expense Tracker` | Application display name |
| `APP_ENV` | `development` | Environment: `development`, `staging`, or `production` |
| `DEBUG` | `true` | Enable debug mode and auto-reload |
| `HOST` | `127.0.0.1` | Server bind host |
| `PORT` | `8000` | Server bind port |
| `DATABASE_URL` | `postgresql+psycopg2://postgres:postgres@localhost:5432/expense_tracker` | SQLAlchemy database URL |
| `SECRET_KEY` | *(placeholder)* | Secret for signing session cookies — **change in production** |
| `SESSION_COOKIE_NAME` | `expense_tracker_session` | Session cookie name |
| `SESSION_MAX_AGE` | `86400` | Session lifetime in seconds (24 hours) |
| `LOG_LEVEL` | `INFO` | Logging level |

---

## Running Migrations

All commands run from the project root:

```bash
# Apply all pending migrations
alembic upgrade head

# Show current revision
alembic current

# View migration history
alembic history

# Roll back one revision
alembic downgrade -1
```

Current head: **`001_initial_schema`** — creates `users`, `user_profiles`, `categories`, and `transactions`.

---

## Running Tests

Tests use an **in-memory SQLite** database automatically — PostgreSQL is not required to run the test suite.

```bash
pytest -q
```

Run a specific test file:

```bash
pytest tests/integration/test_categories.py -v
pytest tests/integration/test_transactions.py -v
pytest tests/integration/test_auth.py -v
```

**Test coverage includes:**

- Authentication (login, signup, logout, session protection)
- Category CRUD, duplicate prevention, default seeding
- Transaction CRUD, pagination, validation
- Database connectivity and health checks

---

## Screenshots

> Add screenshots to a `docs/screenshots/` folder and update the paths below.

| Screen | Preview |
|--------|---------|
| Login | ![Login screen](docs/screenshots/login.png) |
| Add Expense | ![Add Expense screen](docs/screenshots/add-expense.png) |
| Settings (Categories) | ![Settings screen](docs/screenshots/settings.png) |
| Dashboard (placeholder) | ![Dashboard screen](docs/screenshots/dashboard.png) |

---

## Current Project Status

| Area | Status |
|------|--------|
| FastAPI application scaffolding | ✅ Complete |
| PostgreSQL integration & migrations | ✅ Complete |
| Session authentication (register / login / logout) | ✅ Complete |
| Category CRUD (API + Settings UI) | ✅ Complete |
| Transaction CRUD (API + Add Expense UI) | ✅ Complete |
| Default category seeding | ✅ Complete |
| Sidebar navigation | ✅ Complete |
| Automated test suite (48 tests) | ✅ Complete |
| Dashboard metrics & charts | ⏳ Placeholder only |
| Reports & analytics | ⏳ Placeholder only |
| Profile settings UI | ⏳ Not started (`user_profiles` table exists) |
| Production security hardening | ⏳ Not started |

---

## Planned Features

The following are **not yet implemented** and are planned for upcoming phases:

- **Dashboard** — Live balance, income, expense, and savings summaries wired to transaction data
- **Charts** — Visual breakdowns of spending and income (Chart.js integration)
- **Reports** — Filterable analytics, date-range reports, and export options
- **Profile Settings** — Update currency, monthly salary, and account preferences via UI
- **Security Hardening** — Production cookie settings, rate limiting, CSRF for forms, secrets management, and deployment hardening

---

## License

No license file is included yet. Add one before public distribution.
