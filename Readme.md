# Finance Dashboard API

A backend system for managing financial records with role-based access control, built with FastAPI and SQLite.

## Live Demo

- **API Base URL:** `https://finance-dashboard.onrender.com`
- **Interactive Docs (Swagger UI):** `https://finance-dashboard.onrender.com/docs`

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Language | Python 3.11 |
| Framework | FastAPI |
| Database | SQLite (via SQLAlchemy ORM) |
| Auth | JWT (python-jose + passlib bcrypt) |
| Rate Limiting | slowapi |
| Docs | Swagger UI (auto-generated) |
| Hosting | Render.com |

---

## Features

- JWT Authentication with Bearer tokens
- Role-based access control (Viewer / Analyst / Admin)
- Financial records CRUD with soft delete and restore
- Dashboard summary APIs (totals, trends, category breakdown)
- Filtering by type, category, date range, and search keyword
- Pagination on all record listings
- Input validation with meaningful error responses
- Auto-seeded test users and sample data on startup
- Rate limiting on auth endpoints
- Interactive Swagger UI documentation

---

## Default Test Users

| Email | Password | Role |
|-------|----------|------|
| admin@finance.com | admin123 | Admin |
| analyst@finance.com | analyst123 | Analyst |
| viewer@finance.com | viewer123 | Viewer |

---

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/finance-dashboard.git
cd finance-dashboard
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the server

```bash
uvicorn main:app --reload
```

### 5. Open API docs

```
http://localhost:8000/docs
```

---

## How to Authenticate

1. Go to `/docs`
2. Click `POST /auth/login`
3. Enter email and password
4. Copy the `access_token` from the response
5. Click the **Authorize** button at the top of the page
6. Paste the token and click **Authorize**
7. All subsequent requests will use this token

---

## API Endpoints

### Auth
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/auth/login` | Public | Login and get JWT token |

### Users
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/users/` | Admin | Create a new user |
| GET | `/users/` | Admin | Get all users (filter by role, status) |
| GET | `/users/me/profile` | All | Get your own profile |
| GET | `/users/{id}` | Admin | Get user by ID |
| PATCH | `/users/{id}` | Admin | Update user role or status |
| DELETE | `/users/{id}` | Admin | Delete a user |

### Financial Records
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/records/` | Admin | Create a financial record |
| GET | `/records/` | All | Get all records with filters + pagination |
| GET | `/records/{id}` | All | Get a single record |
| PUT | `/records/{id}` | Admin | Update a record |
| DELETE | `/records/{id}` | Admin | Soft delete a record |
| PATCH | `/records/{id}/restore` | Admin | Restore a soft deleted record |

### Dashboard
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/dashboard/summary` | Analyst + Admin | Total income, expenses, net balance, categories |
| GET | `/dashboard/trends` | Analyst + Admin | Monthly income vs expense trends |
| GET | `/dashboard/categories` | Analyst + Admin | Category-wise totals |
| GET | `/dashboard/recent` | All | Recent financial activity |

---

## Query Parameters

### GET /records/
| Parameter | Type | Description |
|-----------|------|-------------|
| type | string | Filter by `income` or `expense` |
| category | string | Filter by category name |
| search | string | Search in notes or category |
| date_from | datetime | Start date filter |
| date_to | datetime | End date filter |
| page | int | Page number (default: 1) |
| page_size | int | Records per page (default: 10, max: 100) |

---

## Role Permissions

| Endpoint | Viewer | Analyst | Admin |
|----------|--------|---------|-------|
| Login | ✅ | ✅ | ✅ |
| View records | ✅ | ✅ | ✅ |
| View recent activity | ✅ | ✅ | ✅ |
| View dashboard summary | ❌ | ✅ | ✅ |
| View trends & categories | ❌ | ✅ | ✅ |
| Create / Update / Delete records | ❌ | ❌ | ✅ |
| Manage users | ❌ | ❌ | ✅ |

---

## Project Structure

```
finance-dashboard/
├── main.py              # App entry point, startup seed, auth route
├── database.py          # SQLite engine, ORM models, DB session
├── models.py            # Pydantic schemas for request/response validation
├── auth.py              # JWT creation, password hashing, user seeding
├── middleware.py        # Role-based access control dependencies
├── routers/
│   ├── users.py         # User management endpoints
│   ├── records.py       # Financial records CRUD endpoints
│   └── dashboard.py     # Summary and analytics endpoints
├── requirements.txt
└── README.md
```

---

## Assumptions Made

- Amounts are always positive. The `type` field (income/expense) determines direction.
- Soft delete is used for records — deleted records are hidden from all GET endpoints but can be restored by an admin.
- Admin cannot deactivate or delete their own account to prevent lockout.
- SQLite resets on Render free tier restarts — the seed script auto-repopulates tables and test data on every startup.
- JWT tokens expire after 24 hours.
- Rate limiting is applied on the login endpoint (10 requests/minute per IP).

---

## Deployment (Render.com)

1. Push code to GitHub
2. Go to [render.com](https://render.com) and create a new **Web Service**
3. Connect your GitHub repository
4. Set the following:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port 10000`
5. Click **Deploy**
6. Your API will be live at `https://your-service-name.onrender.com`

---

## Author

**Manohar Poleboina**
B.Tech Computer Science — Vignan Institute of Technology and Science, Hyderabad
