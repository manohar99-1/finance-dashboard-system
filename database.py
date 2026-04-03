from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, Enum
from sqlalchemy.orm import declarative_basefrom sqlalchemy.orm import sessionmaker
from datetime import datetime
import enum

DATABASE_URL = "sqlite:///./finance.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# --- Enums ---
class UserRole(str, enum.Enum):
    viewer = "viewer"
    analyst = "analyst"
    admin = "admin"

class TransactionType(str, enum.Enum):
    income = "income"
    expense = "expense"


# --- User Model ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default=UserRole.viewer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# --- Financial Record Model ---
class FinancialRecord(Base):
    __tablename__ = "financial_records"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    type = Column(String(10), nullable=False)  # income or expense
    category = Column(String(100), nullable=False)
    date = Column(DateTime, nullable=False)
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, nullable=False)  # user id
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# --- DB Session Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
