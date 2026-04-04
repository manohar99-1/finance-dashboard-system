from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from database import Base, engine, get_db, User, FinancialRecord
from models import TokenResponse
from auth import verify_password, create_access_token, seed_users
from routers import users, records, dashboard
from datetime import datetime

# --- Rate Limiter Setup ---
limiter = Limiter(key_func=get_remote_address)


# --- Seed Sample Financial Records ---
def seed_records(db: Session):
    existing = db.query(FinancialRecord).count()
    if existing > 0:
        return

    sample_records = [
        {"amount": 5000.0, "type": "income", "category": "Salary", "date": datetime(2024, 1, 1), "notes": "January salary"},
        {"amount": 1200.0, "type": "expense", "category": "Rent", "date": datetime(2024, 1, 5), "notes": "Monthly rent"},
        {"amount": 300.0, "type": "expense", "category": "Groceries", "date": datetime(2024, 1, 10), "notes": "Weekly groceries"},
        {"amount": 800.0, "type": "income", "category": "Freelance", "date": datetime(2024, 2, 1), "notes": "Web design project"},
        {"amount": 150.0, "type": "expense", "category": "Utilities", "date": datetime(2024, 2, 5), "notes": "Electricity bill"},
        {"amount": 5000.0, "type": "income", "category": "Salary", "date": datetime(2024, 2, 1), "notes": "February salary"},
        {"amount": 500.0, "type": "expense", "category": "Transport", "date": datetime(2024, 2, 15), "notes": "Monthly commute"},
        {"amount": 1200.0, "type": "expense", "category": "Rent", "date": datetime(2024, 2, 5), "notes": "Monthly rent"},
        {"amount": 2000.0, "type": "income", "category": "Bonus", "date": datetime(2024, 3, 1), "notes": "Performance bonus"},
        {"amount": 400.0, "type": "expense", "category": "Groceries", "date": datetime(2024, 3, 10), "notes": "Monthly groceries"},
    ]

    admin = db.query(User).filter(User.email == "admin@finance.com").first()
    if not admin:
        return

    for r in sample_records:
        db.add(FinancialRecord(
            amount=r["amount"],
            type=r["type"],
            category=r["category"],
            date=r["date"],
            notes=r["notes"],
            created_by=admin.id
        ))
    db.commit()


# --- Lifespan (replaces on_event startup) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        seed_users(db)
        seed_records(db)
    finally:
        db.close()
    yield


# --- App Init ---
app = FastAPI(
    title="Finance Dashboard API",
    lifespan=lifespan,
    description="""
## Finance Data Processing and Access Control Backend

A backend system for managing financial records with role-based access control.

### Roles
- **Viewer** — Can view records and recent activity
- **Analyst** — Can view records and access dashboard summaries
- **Admin** — Full access to all endpoints

### Default Test Users
| Email | Password | Role |
|-------|----------|------|
| admin@finance.com | admin123 | Admin |
| analyst@finance.com | analyst123 | Analyst |
| viewer@finance.com | viewer123 | Viewer |

### How to Authenticate
1. Click the `/auth/login` endpoint
2. Enter email and password
3. Copy the `access_token` from response
4. Click **Authorize** button at the top
5. Paste token and click Authorize
    """,
    version="1.0.0",
)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Rate Limit Error Handler ---
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# --- Auth Route ---
@app.post("/auth/login", response_model=TokenResponse, tags=["Auth"])
@limiter.limit("10/minute")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is inactive. Contact an admin."
        )

    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


# --- Health Check ---
@app.get("/", tags=["Health"])
def root():
    return {
        "status": "running",
        "message": "Finance Dashboard API is live",
        "docs": "/docs",
        "version": "1.0.0"
    }


# --- Include Routers ---
app.include_router(users.router)
app.include_router(records.router)
app.include_router(dashboard.router)
