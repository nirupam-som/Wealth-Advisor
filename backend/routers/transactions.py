"""
Transactions router – query and summarize user transactions.

Endpoints:
    GET /transactions/           – List transactions (with filters).
    GET /transactions/summary    – Aggregated income / expense / category breakdown.
    GET /transactions/categories – Unique category list.
"""

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Transaction
from backend.schemas import TransactionResponse, TransactionSummary

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("/", response_model=list[TransactionResponse])
def list_transactions(
    user_id: int = Query(default=1, description="User ID"),
    category: str | None = Query(default=None, description="Filter by category"),
    start_date: date | None = Query(default=None, description="Start date (inclusive)"),
    end_date: date | None = Query(default=None, description="End date (inclusive)"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[TransactionResponse]:
    """Return transactions for a user with optional filters.

    Supports filtering by **category**, **start_date**, and **end_date**.
    Results are ordered newest-first and support pagination via
    ``limit`` / ``offset``.
    """
    query = db.query(Transaction).filter(Transaction.user_id == user_id)

    if category:
        query = query.filter(Transaction.category == category)
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)

    transactions = (
        query.order_by(Transaction.date.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [TransactionResponse.model_validate(t) for t in transactions]


@router.get("/summary", response_model=TransactionSummary)
def get_transaction_summary(
    user_id: int = Query(default=1, description="User ID"),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
) -> TransactionSummary:
    """Return an aggregated spending summary for a user.

    Calculates total income, total expenses, net amount, transaction
    count, and a per-category breakdown of expenses.
    """
    query = db.query(Transaction).filter(Transaction.user_id == user_id)
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)

    transactions = query.all()

    total_income = 0.0
    total_expense = 0.0
    category_breakdown: dict[str, float] = {}

    for txn in transactions:
        if txn.transaction_type == "credit":
            total_income += txn.amount
        else:
            total_expense += txn.amount
            cat = txn.category or "Uncategorized"
            category_breakdown[cat] = category_breakdown.get(cat, 0.0) + txn.amount

    return TransactionSummary(
        total_income=round(total_income, 2),
        total_expense=round(total_expense, 2),
        net=round(total_income - total_expense, 2),
        category_breakdown={k: round(v, 2) for k, v in category_breakdown.items()},
        transaction_count=len(transactions),
    )


@router.get("/categories", response_model=list[str])
def get_categories(
    user_id: int = Query(default=1, description="User ID"),
    db: Session = Depends(get_db),
) -> list[str]:
    """Return a sorted list of unique transaction categories for a user."""
    rows = (
        db.query(Transaction.category)
        .filter(Transaction.user_id == user_id)
        .filter(Transaction.category.isnot(None))
        .distinct()
        .all()
    )
    return sorted(row[0] for row in rows if row[0])
