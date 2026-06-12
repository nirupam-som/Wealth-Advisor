"""
FastAPI application entry-point for the AI Wealth Advisor.

Registers all routers, sets up CORS, initialises the database on
startup, and creates a default user if one doesn't already exist.

Run with::

    uvicorn backend.main:app --reload
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import SessionLocal, init_db
from backend.models import User
from backend.routers import chat, goals, insights, transactions, upload

logger = logging.getLogger(__name__)


# ── Lifespan (startup / shutdown) ──────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler.

    * Creates all database tables.
    * Ensures a default user (id=1) exists.
    """
    logger.info("Initialising database …")
    init_db()

    # Seed default user.
    db: Session = SessionLocal()
    try:
        existing = db.query(User).filter(User.id == 1).first()
        if not existing:
            default_user = User(
                id=1,
                username="default",
                email="user@example.com",
                created_at=datetime.utcnow(),
            )
            db.add(default_user)
            db.commit()
            logger.info("Default user created (id=1).")
        else:
            logger.info("Default user already exists.")
    finally:
        db.close()

    logger.info("🚀 %s is ready.", settings.APP_NAME)
    yield  # ← application runs here
    logger.info("Shutting down …")


# ── Application ────────────────────────────────────────────────────────

app = FastAPI(
    title="AI Wealth Advisor API",
    description=(
        "An AI-powered personal finance assistant that analyses bank "
        "statements, tracks goals, evaluates portfolio risk, and provides "
        "actionable financial insights via Google Gemini."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS (allow everything for local development) ──────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────

app.include_router(upload.router)
app.include_router(transactions.router)
app.include_router(goals.router)
app.include_router(chat.router)
app.include_router(insights.router)


# ── Health check ───────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def health_check() -> dict:
    """Root health-check endpoint.

    Returns the application name, version, and status.
    """
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "status": "healthy",
    }
