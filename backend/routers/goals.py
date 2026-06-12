"""
Goals router – full CRUD for financial goals.

Endpoints:
    POST   /goals/          – Create a new goal.
    GET    /goals/          – List all goals for a user.
    GET    /goals/{goal_id} – Get a single goal by ID.
    PUT    /goals/{goal_id} – Update an existing goal.
    DELETE /goals/{goal_id} – Delete a goal.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Goal
from backend.schemas import GoalCreate, GoalResponse, GoalUpdate

router = APIRouter(prefix="/goals", tags=["Goals"])


@router.post("/", response_model=GoalResponse, status_code=201)
def create_goal(
    payload: GoalCreate,
    db: Session = Depends(get_db),
) -> GoalResponse:
    """Create a new financial goal."""
    goal = Goal(
        user_id=payload.user_id,
        name=payload.name,
        target_amount=payload.target_amount,
        current_amount=payload.current_amount,
        deadline=payload.deadline,
        priority=payload.priority,
        status=payload.status,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return GoalResponse.model_validate(goal)


@router.get("/", response_model=list[GoalResponse])
def list_goals(
    user_id: int = Query(default=1, description="User ID"),
    status: str | None = Query(default=None, description="Filter by status"),
    db: Session = Depends(get_db),
) -> list[GoalResponse]:
    """List all financial goals for a user, optionally filtered by status."""
    query = db.query(Goal).filter(Goal.user_id == user_id)

    if status:
        query = query.filter(Goal.status == status)

    goals = query.order_by(Goal.created_at.desc()).all()
    return [GoalResponse.model_validate(g) for g in goals]


@router.get("/{goal_id}", response_model=GoalResponse)
def get_goal(
    goal_id: int,
    db: Session = Depends(get_db),
) -> GoalResponse:
    """Retrieve a single goal by its ID."""
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail=f"Goal {goal_id} not found.")
    return GoalResponse.model_validate(goal)


@router.put("/{goal_id}", response_model=GoalResponse)
def update_goal(
    goal_id: int,
    payload: GoalUpdate,
    db: Session = Depends(get_db),
) -> GoalResponse:
    """Update an existing goal.

    Only the fields present in the request body are updated; all others
    are left unchanged.
    """
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail=f"Goal {goal_id} not found.")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(goal, field, value)

    db.commit()
    db.refresh(goal)
    return GoalResponse.model_validate(goal)


@router.delete("/{goal_id}", status_code=204)
def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Delete a financial goal."""
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail=f"Goal {goal_id} not found.")

    db.delete(goal)
    db.commit()
