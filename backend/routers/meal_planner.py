from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List
import crud, models, schemas, database, services

router = APIRouter(
    prefix="/meal-planner",
    tags=["meal-planner"],
)

@router.post("/generate-shopping-list")
def generate_shopping_list(recipe_ids: List[int] = Body(...), db: Session = Depends(database.get_db)):
    recipes = []
    for r_id in recipe_ids:
        recipe = crud.get_recipe(db, r_id)
        if recipe:
            recipes.append(recipe)
    
    shopping_list = services.generate_shopping_list(recipes)
    return shopping_list
