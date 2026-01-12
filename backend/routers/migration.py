from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
import database
import models
import services

router = APIRouter(
    prefix="/migration",
    tags=["migration"],
    responses={404: {"description": "Not found"}},
)

# Track if a migration is currently running
_migration_running = False
_migration_paused = False


class MigrationStatusResponse(BaseModel):
    is_running: bool
    is_paused: bool
    total_recipes: int
    pending: int
    processing: int
    completed: int
    failed: int
    skipped: int


class MigrationResultItem(BaseModel):
    recipe_id: int
    recipe_name: str
    status: str
    original_count: int
    new_count: Optional[int]
    error: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]


class MigrationResultsResponse(BaseModel):
    results: List[MigrationResultItem]
    total: int


@router.post("/start")
async def start_migration(
    background_tasks: BackgroundTasks,
    provider: str = Query("gemini", description="LLM provider: 'openai' or 'gemini'"),
    rate_limit: float = Query(1.0, description="Delay in seconds between API calls"),
    fresh: bool = Query(False, description="If True, clear all previous migration records and start fresh"),
    db: Session = Depends(database.get_db)
):
    """
    Start automatic ingredient migration for all recipes with source_file.

    - Set fresh=True to clear previous progress and start from scratch
    - Set fresh=False (default) to continue from where you left off

    This will:
    1. Fetch each recipe's original PDF from the efarmz CDN
    2. Re-parse using improved prompts
    3. Update ingredients if new_count >= original_count
    """
    global _migration_running, _migration_paused

    if _migration_running:
        raise HTTPException(status_code=409, detail="Migration is already running. Use /pause first.")

    # Validate provider
    provider = provider.lower().strip()
    if provider not in ["openai", "gemini"]:
        raise HTTPException(status_code=400, detail="Invalid provider. Use 'openai' or 'gemini'.")

    # Count eligible recipes (those with source_file)
    eligible_count = db.query(func.count(models.Recipe.id)).filter(
        models.Recipe.source_file.isnot(None),
        models.Recipe.source_file != ""
    ).scalar()

    if eligible_count == 0:
        raise HTTPException(status_code=400, detail="No recipes with source_file found to migrate")

    # Clear previous migration records if fresh start requested
    if fresh:
        db.query(models.IngredientMigration).delete()
        db.commit()
        already_processed = 0
    else:
        # Count already processed recipes
        already_processed = db.query(func.count(models.IngredientMigration.id)).filter(
            models.IngredientMigration.status.in_(["completed", "skipped", "failed"])
        ).scalar()

    _migration_running = True
    _migration_paused = False

    # Start background task
    background_tasks.add_task(
        services.run_ingredient_migration,
        provider,
        rate_limit
    )

    return {
        "status": "started",
        "provider": provider,
        "total_recipes": eligible_count,
        "already_processed": already_processed,
        "remaining": eligible_count - already_processed,
        "rate_limit": rate_limit,
        "fresh_start": fresh
    }


@router.post("/resume")
async def resume_migration(
    background_tasks: BackgroundTasks,
    provider: str = Query("gemini", description="LLM provider: 'openai' or 'gemini'"),
    rate_limit: float = Query(1.0, description="Delay in seconds between API calls"),
    db: Session = Depends(database.get_db)
):
    """
    Resume a paused migration from where it left off.

    This is equivalent to calling /start with fresh=False.
    """
    global _migration_running, _migration_paused

    if _migration_running:
        raise HTTPException(status_code=409, detail="Migration is already running")

    # Validate provider
    provider = provider.lower().strip()
    if provider not in ["openai", "gemini"]:
        raise HTTPException(status_code=400, detail="Invalid provider. Use 'openai' or 'gemini'.")

    # Count eligible recipes
    eligible_count = db.query(func.count(models.Recipe.id)).filter(
        models.Recipe.source_file.isnot(None),
        models.Recipe.source_file != ""
    ).scalar()

    # Count already processed recipes
    already_processed = db.query(func.count(models.IngredientMigration.id)).filter(
        models.IngredientMigration.status.in_(["completed", "skipped", "failed"])
    ).scalar()

    remaining = eligible_count - already_processed
    if remaining <= 0:
        return {
            "status": "already_complete",
            "message": "All recipes have already been processed",
            "total_recipes": eligible_count,
            "already_processed": already_processed
        }

    _migration_running = True
    _migration_paused = False

    # Start background task
    background_tasks.add_task(
        services.run_ingredient_migration,
        provider,
        rate_limit
    )

    return {
        "status": "resumed",
        "provider": provider,
        "total_recipes": eligible_count,
        "already_processed": already_processed,
        "remaining": remaining,
        "rate_limit": rate_limit
    }


@router.get("/status", response_model=MigrationStatusResponse)
def get_migration_status(db: Session = Depends(database.get_db)):
    """Get current migration progress statistics."""
    global _migration_running, _migration_paused

    # Count total eligible recipes
    total_recipes = db.query(func.count(models.Recipe.id)).filter(
        models.Recipe.source_file.isnot(None),
        models.Recipe.source_file != ""
    ).scalar()

    # Count by status
    status_counts = db.query(
        models.IngredientMigration.status,
        func.count(models.IngredientMigration.id)
    ).group_by(models.IngredientMigration.status).all()

    counts = {status: count for status, count in status_counts}

    processed = sum(counts.values())
    pending_in_queue = total_recipes - processed

    return MigrationStatusResponse(
        is_running=_migration_running,
        is_paused=_migration_paused and not _migration_running,
        total_recipes=total_recipes,
        pending=pending_in_queue + counts.get("pending", 0),
        processing=counts.get("processing", 0),
        completed=counts.get("completed", 0),
        failed=counts.get("failed", 0),
        skipped=counts.get("skipped", 0)
    )


@router.get("/results", response_model=MigrationResultsResponse)
def get_migration_results(
    status: Optional[str] = Query(None, description="Filter by status: completed, failed, skipped"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(database.get_db)
):
    """Get detailed migration results with optional filtering."""
    query = db.query(models.IngredientMigration).join(models.Recipe)

    if status:
        query = query.filter(models.IngredientMigration.status == status)

    total = query.count()

    migrations = query.order_by(
        models.IngredientMigration.completed_at.desc().nullsfirst()
    ).offset(skip).limit(limit).all()

    results = []
    for m in migrations:
        results.append(MigrationResultItem(
            recipe_id=m.recipe_id,
            recipe_name=m.recipe.name if m.recipe else "Unknown",
            status=m.status,
            original_count=m.original_count,
            new_count=m.new_count,
            error=m.error,
            created_at=m.created_at,
            completed_at=m.completed_at
        ))

    return MigrationResultsResponse(results=results, total=total)


@router.post("/pause")
def pause_migration():
    """Pause the migration after the current recipe. Can be resumed later with /resume."""
    global _migration_running, _migration_paused

    if not _migration_running:
        raise HTTPException(status_code=400, detail="No migration is currently running")

    _migration_running = False
    _migration_paused = True
    return {
        "status": "pausing",
        "message": "Migration will pause after current recipe completes. Use /resume to continue."
    }


@router.post("/reset")
def reset_migration(db: Session = Depends(database.get_db)):
    """Clear all migration records to start fresh."""
    global _migration_running, _migration_paused

    if _migration_running:
        raise HTTPException(status_code=409, detail="Cannot reset while migration is running. Pause first.")

    count = db.query(models.IngredientMigration).delete()
    db.commit()

    _migration_paused = False

    return {
        "status": "reset",
        "message": f"Cleared {count} migration records"
    }


def set_migration_running(running: bool):
    """Called by services.py to update migration status."""
    global _migration_running
    _migration_running = running


def is_migration_running() -> bool:
    """Check if migration should continue running."""
    global _migration_running
    return _migration_running
