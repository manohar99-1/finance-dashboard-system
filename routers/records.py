from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db, FinancialRecord
from models import RecordCreate, RecordUpdate, RecordResponse, PaginatedRecords
from database import User
from middleware import admin_only, any_authenticated_user
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/records", tags=["Financial Records"])


# --- Create Record (Admin only) ---
@router.post("/", response_model=RecordResponse, status_code=status.HTTP_201_CREATED)
def create_record(
    payload: RecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only)
):
    record = FinancialRecord(
        amount=payload.amount,
        type=payload.type,
        category=payload.category,
        date=payload.date,
        notes=payload.notes,
        created_by=current_user.id
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


# --- Get All Records (All roles, with filters + pagination) ---
@router.get("/", response_model=PaginatedRecords)
def get_records(
    # Filters
    type: Optional[str] = Query(None, description="income or expense"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in notes or category"),
    date_from: Optional[datetime] = Query(None, description="Start date filter"),
    date_to: Optional[datetime] = Query(None, description="End date filter"),
    # Pagination
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Records per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(any_authenticated_user)
):
    query = db.query(FinancialRecord).filter(FinancialRecord.is_deleted == False)

    # Apply filters
    if type:
        query = query.filter(FinancialRecord.type == type)
    if category:
        query = query.filter(FinancialRecord.category.ilike(f"%{category}%"))
    if search:
        query = query.filter(
            or_(
                FinancialRecord.notes.ilike(f"%{search}%"),
                FinancialRecord.category.ilike(f"%{search}%")
            )
        )
    if date_from:
        query = query.filter(FinancialRecord.date >= date_from)
    if date_to:
        query = query.filter(FinancialRecord.date <= date_to)

    # Total count before pagination
    total = query.count()

    # Apply pagination
    records = query.order_by(FinancialRecord.date.desc()) \
                   .offset((page - 1) * page_size) \
                   .limit(page_size) \
                   .all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "records": records
    }


# --- Get Single Record (All roles) ---
@router.get("/{record_id}", response_model=RecordResponse)
def get_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(any_authenticated_user)
):
    record = db.query(FinancialRecord).filter(
        FinancialRecord.id == record_id,
        FinancialRecord.is_deleted == False
    ).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Record with id {record_id} not found."
        )
    return record


# --- Update Record (Admin only) ---
@router.put("/{record_id}", response_model=RecordResponse)
def update_record(
    record_id: int,
    payload: RecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only)
):
    record = db.query(FinancialRecord).filter(
        FinancialRecord.id == record_id,
        FinancialRecord.is_deleted == False
    ).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Record with id {record_id} not found."
        )

    if payload.amount is not None:
        record.amount = payload.amount
    if payload.type is not None:
        record.type = payload.type
    if payload.category is not None:
        record.category = payload.category
    if payload.date is not None:
        record.date = payload.date
    if payload.notes is not None:
        record.notes = payload.notes

    record.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(record)
    return record


# --- Soft Delete Record (Admin only) ---
@router.delete("/{record_id}", status_code=status.HTTP_200_OK)
def delete_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only)
):
    record = db.query(FinancialRecord).filter(
        FinancialRecord.id == record_id,
        FinancialRecord.is_deleted == False
    ).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Record with id {record_id} not found."
        )

    # Soft delete — just mark as deleted, don't remove from DB
    record.is_deleted = True
    record.updated_at = datetime.utcnow()
    db.commit()

    return {"message": f"Record {record_id} deleted successfully."}


# --- Restore Soft Deleted Record (Admin only) ---
@router.patch("/{record_id}/restore", response_model=RecordResponse)
def restore_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only)
):
    record = db.query(FinancialRecord).filter(
        FinancialRecord.id == record_id,
        FinancialRecord.is_deleted == True
    ).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deleted record with id {record_id} not found."
        )

    record.is_deleted = False
    record.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(record)
    return record
