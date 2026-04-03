from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db, FinancialRecord
from models import DashboardSummary, CategorySummary, MonthlyTrend, RecordResponse
from database import User
from middleware import analyst_or_admin, any_authenticated_user
from datetime import datetime
from typing import Optional, List

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


# --- Full Summary (Analyst + Admin) ---
@router.get("/summary", response_model=DashboardSummary)
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(analyst_or_admin)
):
    active_records = db.query(FinancialRecord).filter(FinancialRecord.is_deleted == False)

    total_income = db.query(func.sum(FinancialRecord.amount)).filter(
        FinancialRecord.is_deleted == False,
        FinancialRecord.type == "income"
    ).scalar() or 0.0

    total_expenses = db.query(func.sum(FinancialRecord.amount)).filter(
        FinancialRecord.is_deleted == False,
        FinancialRecord.type == "expense"
    ).scalar() or 0.0

    net_balance = total_income - total_expenses
    total_records = active_records.count()

    # Category wise totals
    category_data = db.query(
        FinancialRecord.category,
        func.sum(FinancialRecord.amount).label("total")
    ).filter(
        FinancialRecord.is_deleted == False
    ).group_by(FinancialRecord.category).all()

    category_totals = [
        CategorySummary(category=row.category, total=row.total)
        for row in category_data
    ]

    # Recent 5 activities
    recent = active_records.order_by(
        FinancialRecord.created_at.desc()
    ).limit(5).all()

    return DashboardSummary(
        total_income=total_income,
        total_expenses=total_expenses,
        net_balance=net_balance,
        total_records=total_records,
        category_totals=category_totals,
        recent_activity=recent
    )


# --- Monthly Trends (Analyst + Admin) ---
@router.get("/trends", response_model=List[MonthlyTrend])
def get_trends(
    year: Optional[int] = Query(None, description="Filter by year e.g. 2024"),
    db: Session = Depends(get_db),
    current_user: User = Depends(analyst_or_admin)
):
    query = db.query(FinancialRecord).filter(FinancialRecord.is_deleted == False)

    if year:
        query = query.filter(func.strftime("%Y", FinancialRecord.date) == str(year))

    records = query.all()

    # Group by month manually
    trends = {}
    for r in records:
        month_key = r.date.strftime("%Y-%m")
        if month_key not in trends:
            trends[month_key] = {"income": 0.0, "expense": 0.0}
        if r.type == "income":
            trends[month_key]["income"] += r.amount
        else:
            trends[month_key]["expense"] += r.amount

    return [
        MonthlyTrend(month=month, income=data["income"], expense=data["expense"])
        for month, data in sorted(trends.items())
    ]


# --- Category Breakdown (Analyst + Admin) ---
@router.get("/categories", response_model=List[CategorySummary])
def get_category_breakdown(
    type: Optional[str] = Query(None, description="income or expense"),
    db: Session = Depends(get_db),
    current_user: User = Depends(analyst_or_admin)
):
    query = db.query(
        FinancialRecord.category,
        func.sum(FinancialRecord.amount).label("total")
    ).filter(FinancialRecord.is_deleted == False)

    if type:
        query = query.filter(FinancialRecord.type == type)

    results = query.group_by(FinancialRecord.category).all()

    return [
        CategorySummary(category=row.category, total=row.total)
        for row in results
    ]


# --- Recent Activity (All roles) ---
@router.get("/recent", response_model=List[RecordResponse])
def get_recent_activity(
    limit: int = Query(10, ge=1, le=50, description="Number of recent records"),
    db: Session = Depends(get_db),
    current_user: User = Depends(any_authenticated_user)
):
    records = db.query(FinancialRecord).filter(
        FinancialRecord.is_deleted == False
    ).order_by(FinancialRecord.created_at.desc()).limit(limit).all()

    return records
