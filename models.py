from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from database import UserRole, TransactionType


# ─── Auth ───────────────────────────────────────────

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ─── Users ──────────────────────────────────────────

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5)
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.viewer

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Financial Records ───────────────────────────────

class RecordCreate(BaseModel):
    amount: float = Field(..., gt=0, description="Must be greater than 0")
    type: TransactionType
    category: str = Field(..., min_length=2, max_length=100)
    date: datetime
    notes: Optional[str] = Field(None, max_length=500)

class RecordUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    type: Optional[TransactionType] = None
    category: Optional[str] = Field(None, min_length=2, max_length=100)
    date: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=500)

class RecordResponse(BaseModel):
    id: int
    amount: float
    type: str
    category: str
    date: datetime
    notes: Optional[str]
    created_by: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─── Dashboard ───────────────────────────────────────

class CategorySummary(BaseModel):
    category: str
    total: float

class MonthlyTrend(BaseModel):
    month: str
    income: float
    expense: float

class DashboardSummary(BaseModel):
    total_income: float
    total_expenses: float
    net_balance: float
    total_records: int
    category_totals: list[CategorySummary]
    recent_activity: list[RecordResponse]


# ─── Pagination ──────────────────────────────────────

class PaginatedRecords(BaseModel):
    total: int
    page: int
    page_size: int
    records: list[RecordResponse]
