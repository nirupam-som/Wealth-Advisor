"""
Pydantic v2 request / response schemas.

Every schema that may be returned from an ORM model has
``model_config = ConfigDict(from_attributes=True)`` so
``model_validate(orm_obj)`` works without manual conversion.
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ═══════════════════════════════════════════════════════════════════════
# User
# ═══════════════════════════════════════════════════════════════════════

class UserCreate(BaseModel):
    """Payload for creating a new user."""

    username: str = Field(..., min_length=1, max_length=50)
    email: EmailStr


class UserResponse(BaseModel):
    """User data returned to the client."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    created_at: datetime


# ═══════════════════════════════════════════════════════════════════════
# Transaction
# ═══════════════════════════════════════════════════════════════════════

class TransactionCreate(BaseModel):
    """Payload for manually creating a transaction."""

    user_id: int = 1
    date: date
    description: str = Field(..., min_length=1, max_length=500)
    amount: float = Field(..., gt=0)
    category: str | None = None
    transaction_type: str = Field(..., pattern=r"^(credit|debit)$")
    source_file: str | None = None


class TransactionResponse(BaseModel):
    """Single transaction returned to the client."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    date: date
    description: str
    amount: float
    category: str | None
    transaction_type: str
    source_file: str | None
    created_at: datetime


class TransactionSummary(BaseModel):
    """Aggregated spending summary."""

    total_income: float = 0.0
    total_expense: float = 0.0
    net: float = 0.0
    category_breakdown: dict[str, float] = Field(default_factory=dict)
    transaction_count: int = 0


# ═══════════════════════════════════════════════════════════════════════
# Goal
# ═══════════════════════════════════════════════════════════════════════

class GoalCreate(BaseModel):
    """Payload for creating a financial goal."""

    user_id: int = 1
    name: str = Field(..., min_length=1, max_length=200)
    target_amount: float = Field(..., gt=0)
    current_amount: float = Field(default=0.0, ge=0)
    deadline: date | None = None
    priority: str = Field(default="medium", pattern=r"^(high|medium|low)$")
    status: str = Field(default="active", pattern=r"^(active|completed|paused)$")


class GoalUpdate(BaseModel):
    """Payload for updating an existing goal (all fields optional)."""

    name: str | None = Field(default=None, min_length=1, max_length=200)
    target_amount: float | None = Field(default=None, gt=0)
    current_amount: float | None = Field(default=None, ge=0)
    deadline: date | None = None
    priority: str | None = Field(default=None, pattern=r"^(high|medium|low)$")
    status: str | None = Field(default=None, pattern=r"^(active|completed|paused)$")


class GoalResponse(BaseModel):
    """Goal data returned to the client."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    target_amount: float
    current_amount: float
    deadline: date | None
    priority: str
    status: str
    created_at: datetime


# ═══════════════════════════════════════════════════════════════════════
# Portfolio
# ═══════════════════════════════════════════════════════════════════════

class PortfolioCreate(BaseModel):
    """Payload for adding a portfolio holding."""

    user_id: int = 1
    asset_name: str = Field(..., min_length=1, max_length=200)
    asset_type: str = Field(
        ...,
        pattern=r"^(equity|mutual_fund|fixed_deposit|ppf|gold|crypto)$",
    )
    quantity: float = Field(..., gt=0)
    purchase_price: float = Field(..., ge=0)
    current_price: float = Field(..., ge=0)
    purchase_date: date | None = None


class PortfolioResponse(BaseModel):
    """Single portfolio holding returned to the client."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    asset_name: str
    asset_type: str
    quantity: float
    purchase_price: float
    current_price: float
    purchase_date: date | None
    created_at: datetime


class PortfolioSummary(BaseModel):
    """Aggregated portfolio overview."""

    total_invested: float = 0.0
    total_current_value: float = 0.0
    total_gain_loss: float = 0.0
    gain_loss_pct: float = 0.0
    holdings_count: int = 0
    asset_allocation: dict[str, float] = Field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════════════
# Chat
# ═══════════════════════════════════════════════════════════════════════

class ChatRequest(BaseModel):
    """Payload for sending a message to the AI assistant."""

    user_id: int = 1
    message: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    """AI assistant reply."""

    user_message: str
    assistant_message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ═══════════════════════════════════════════════════════════════════════
# File upload
# ═══════════════════════════════════════════════════════════════════════

class FileUploadResponse(BaseModel):
    """Response after uploading and processing a bank statement."""

    filename: str
    transactions_imported: int
    message: str


# ═══════════════════════════════════════════════════════════════════════
# Insights
# ═══════════════════════════════════════════════════════════════════════

class InsightResponse(BaseModel):
    """AI-generated financial insight."""

    insight_type: str
    content: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict | None = None
