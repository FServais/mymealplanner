from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import database
import models
import schemas
import crud

router = APIRouter(
    prefix="/meal-plans",
    tags=["meal-plans"],
)

@router.post("/", response_model=schemas.MealPlan)
def create_meal_plan(meal_plan: schemas.MealPlanCreate, db: Session = Depends(database.get_db)):
    return crud.create_meal_plan(db=db, meal_plan=meal_plan)

@router.get("/", response_model=List[schemas.MealPlan])
def read_meal_plans(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    return crud.get_meal_plans(db, skip=skip, limit=limit)

@router.get("/{meal_plan_id}", response_model=schemas.MealPlan)
def read_meal_plan(meal_plan_id: int, db: Session = Depends(database.get_db)):
    db_meal_plan = crud.get_meal_plan(db, meal_plan_id=meal_plan_id)
    if db_meal_plan is None:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    return db_meal_plan

@router.delete("/{meal_plan_id}", status_code=204)
def delete_meal_plan(meal_plan_id: int, db: Session = Depends(database.get_db)):
    success = crud.delete_meal_plan(db, meal_plan_id=meal_plan_id)
    if not success:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    return None
