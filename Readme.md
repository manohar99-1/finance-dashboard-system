# Finance Dashboard API

A backend API for managing financial records with role-based access control. Built with FastAPI, SQLite, and JWT authentication.

## Live

- API: https://finance-dashboard-system-duhm.onrender.com
- Docs: https://finance-dashboard-system-duhm.onrender.com/docs

---

## Stack

- Python 3.11 + FastAPI
- SQLite via SQLAlchemy
- JWT auth with python-jose and passlib
- Rate limiting with slowapi
- Hosted on Render.com

---

## Getting Started

```bash
git clone https://github.com/manohar99-1/finance-dashboard-system.git
cd finance-dashboard-system

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
uvicorn main:app --reload
```

Open http://localhost:8000/docs to explore the API.

---

## How to Test

The easiest way is through the Swagger UI at /docs.

1. Use POST /auth/login with one of the test accounts below
2. Copy the access_token from the response
3. Click Authorize at the top of the page, paste the token, and click Authorize
4. Now you can call any endpoint

**Test accounts**

| Email | Password | Role |
|-------|----------|------|
| admin@finance.com | admin123 | Admin |
| analyst@finance.com | analyst123 | Analyst |
| viewer@finance.com | viewer123 | Viewer |

---

## What It Does

The system has three roles with different levels of access.

**Viewers** can see records and recent activity but nothing else.

**Analysts** get everything a viewer can see plus access to the dashboard summaries — totals, trends, and category breakdowns.

**Admins** have full access. They can create, update, and delete records, manage users, and see everything.

---

## Endpoints

**Auth**
- POST /auth/login — get a JWT token

**Users** (Admin only except profile)
- POST /users/ — create user
- GET /users/ — list all users
- GET /users/me/profile — your own profile
- GET /users/{id} — get user by ID
- PATCH /users/{id} — update role or status
- DELETE /users/{id} — delete user

**Financial Records**
- POST /records/ — create record (Admin)
- GET /records/ — list records with filters and pagination (All)
- GET /records/{id} — get single record (All)
- PUT /records/{id} — update record (Admin)
- DELETE /records/{id} — soft delete (Admin)
- PATCH /records/{id}/restore — restore deleted record (Admin)

**Dashboard**
- GET /dashboard/summary — totals and category breakdown (Analyst + Admin)
- GET /dashboard/trends — monthly income vs expense (Analyst + Admin)
- GET /dashboard/categories — category-wise totals (Analyst + Admin)
- GET /dashboard/recent — recent activity (All)

**Filtering on GET /records/**

You can filter by type (income/expense), category, keyword search, and date range. Pagination is supported with page and page_size parameters.

---

## Project Structure

```
finance-dashboard-system/
├── main.py          # entry point, lifespan, auth route, seed data
├── database.py      # SQLAlchemy models and DB setup
├── models.py        # Pydantic schemas for validation
├── auth.py          # JWT logic, password hashing, user seeding
├── middleware.py    # role-based access control
├── routers/
│   ├── users.py
│   ├── records.py
│   └── dashboard.py
└── requirements.txt
```

---

## Notes and Assumptions

A few decisions I made while building this:

- Record amounts are always stored as positive numbers. The type field (income or expense) handles the direction. This keeps aggregation logic simple.

- Deleted records aren't removed from the database. They're marked with is_deleted=True so they can be restored by an admin if needed.

- Admins can't deactivate or delete their own account. This prevents accidental lockout.

- SQLite on Render's free tier resets when the server spins down. To handle this, the app automatically recreates tables and seeds default users and sample records on every startup.

- JWT tokens expire after 24 hours.

- Login is rate limited to 10 requests per minute per IP.

---

## Deployment Notes

This is deployed on Render's free tier using a public GitHub repo. The build command is:

```
pip install -r requirements.txt
```

Start command:

```
uvicorn main:app --host 0.0.0.0 --port 10000
```

No environment variables are required to run it.

---

Manohar Poleboina
B.Tech CSE — Vignan Institute of Technology and Science, Hyderabad
