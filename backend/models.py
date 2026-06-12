"""
SQLAlchemy ORM models for the AI Wealth Advisor.

All models inherit from the shared ``Base`` declared in :mod:`backend.database`.
Relationships are defined so that a cascade delete on a user removes all
associated child records.
"""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class User(Base):
    """Application user."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    goals: Mapped[list["Goal"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    portfolios: Mapped[list["Portfolio"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    chat_messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Transaction(Base):
    """A single financial transaction (credit or debit)."""

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    transaction_type: Mapped[str] = mapped_column(String(10), nullable=False)  # credit / debit
    source_file: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user: Mapped["User"] = relationship(back_populates="transactions")


class Goal(Base):
    """A user-defined financial goal."""

    __tablename__ = "goals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    target_amount: Mapped[float] = mapped_column(Float, nullable=False)
    current_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    priority: Mapped[str] = mapped_column(String(10), nullable=False, default="medium")  # high/medium/low
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")  # active/completed/paused
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user: Mapped["User"] = relationship(back_populates="goals")


class Portfolio(Base):
    """A single asset holding in a user's investment portfolio."""

    __tablename__ = "portfolios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    asset_name: Mapped[str] = mapped_column(String(200), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(50), nullable=False)  # equity/mutual_fund/fixed_deposit/ppf/gold/crypto
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    purchase_price: Mapped[float] = mapped_column(Float, nullable=False)
    current_price: Mapped[float] = mapped_column(Float, nullable=False)
    purchase_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user: Mapped["User"] = relationship(back_populates="portfolios")


class ChatMessage(Base):
    """A single message in a user's chat history with the AI assistant."""

    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # user / assistant
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user: Mapped["User"] = relationship(back_populates="chat_messages")
