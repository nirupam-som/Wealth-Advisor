"""
Chat router – conversational AI financial assistant.

Endpoints:
    POST /chat/         – Send a message and get an AI reply.
    GET  /chat/history  – Retrieve chat history for a user.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import ChatMessage, Goal, Portfolio, Transaction
from backend.schemas import ChatRequest, ChatResponse
from backend.services.llm_service import chat_response as llm_chat_response

router = APIRouter(prefix="/chat", tags=["Chat"])


def _build_financial_context(user_id: int, db: Session) -> str:
    """Build a concise financial context string for the LLM.

    Aggregates the user's transaction summary, active goals, and
    portfolio overview so the model can give grounded answers.
    """
    # ── Transaction summary ─────────────────────────────────────────
    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id)
        .all()
    )
    total_income = sum(t.amount for t in transactions if t.transaction_type == "credit")
    total_expense = sum(t.amount for t in transactions if t.transaction_type == "debit")

    # ── Goals ───────────────────────────────────────────────────────
    goals = (
        db.query(Goal)
        .filter(Goal.user_id == user_id, Goal.status == "active")
        .all()
    )
    goals_text = "\n".join(
        f"  - {g.name}: target ₹{g.target_amount:,.2f}, saved ₹{g.current_amount:,.2f}, "
        f"priority={g.priority}"
        for g in goals
    ) or "  No active goals."

    # ── Portfolio ───────────────────────────────────────────────────
    holdings = (
        db.query(Portfolio)
        .filter(Portfolio.user_id == user_id)
        .all()
    )
    total_invested = sum(h.quantity * h.purchase_price for h in holdings)
    total_current = sum(h.quantity * h.current_price for h in holdings)

    # ── Recent chat (last 6 messages for continuity) ────────────────
    recent_messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(6)
        .all()
    )
    chat_history = "\n".join(
        f"  {m.role}: {m.content[:200]}"
        for m in reversed(recent_messages)
    ) or "  No prior conversation."

    return (
        f"Total Income: ₹{total_income:,.2f}\n"
        f"Total Expenses: ₹{total_expense:,.2f}\n"
        f"Net Savings: ₹{total_income - total_expense:,.2f}\n"
        f"Transaction Count: {len(transactions)}\n\n"
        f"Active Goals:\n{goals_text}\n\n"
        f"Portfolio: invested ₹{total_invested:,.2f}, "
        f"current value ₹{total_current:,.2f} "
        f"({len(holdings)} holdings)\n\n"
        f"Recent Chat History:\n{chat_history}"
    )


@router.post("/", response_model=ChatResponse)
def send_chat_message(
    payload: ChatRequest,
    db: Session = Depends(get_db),
) -> ChatResponse:
    """Send a message to the AI financial assistant.

    The user's financial data (transactions, goals, portfolio) is
    automatically included as context so the AI can give personalized
    answers.  Both the user message and the assistant reply are persisted.
    """
    context = _build_financial_context(payload.user_id, db)
    
    # RAG - retrieve financial knowledge based on user message
    from backend.services.rag_service import search_knowledge_base
    knowledge = search_knowledge_base(payload.message)
    if knowledge:
        context += f"\n\n--- Financial Knowledge Base ---\n{knowledge}"
        
    assistant_reply = llm_chat_response(payload.message, context)

    # Persist user message.
    user_msg = ChatMessage(
        user_id=payload.user_id,
        role="user",
        content=payload.message,
    )
    db.add(user_msg)

    # Persist assistant reply.
    assistant_msg = ChatMessage(
        user_id=payload.user_id,
        role="assistant",
        content=assistant_reply,
    )
    db.add(assistant_msg)
    db.commit()

    return ChatResponse(
        user_message=payload.message,
        assistant_message=assistant_reply,
    )


@router.get("/history")
def get_chat_history(
    user_id: int = Query(default=1, description="User ID"),
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[dict]:
    """Retrieve the chat history for a user, ordered oldest-first.

    Returns a list of dicts with ``id``, ``role``, ``content``, and
    ``created_at``.
    """
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user_id)
        .order_by(ChatMessage.created_at.asc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "created_at": m.created_at.isoformat(),
        }
        for m in messages
    ]
