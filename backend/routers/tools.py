from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from pydantic import BaseModel
import database
import models
import crud
import services

router = APIRouter(
    prefix="/tools",
    tags=["tools"],
    responses={404: {"description": "Not found"}},
)

class MergeIngredientsRequest(BaseModel):
    target_name: str
    source_names: List[str]

@router.post("/ingredients/merge")
def merge_ingredients(request: MergeIngredientsRequest, db: Session = Depends(database.get_db)):
    """
    Merges multiple ingredients into one target ingredient name.
    Updates all recipes that use any of the source_names to use target_name instead.
    """
    # 1. Update all ingredients with source_names to target_name
    # We need to be careful not to create duplicates within a single recipe.
    # If a recipe has both "Tomate" and "Tomates", and we merge "Tomates" -> "Tomate",
    # we might end up with two "Tomate" entries for the same recipe.
    
    # Strategy:
    # Iterate through all source names.
    # For each source name, find all Ingredient records.
    # For each record, check if the recipe already has an ingredient with target_name.
    # If yes, we might need to merge quantities (complex) or just drop the duplicate.
    # For simplicity in this v1: 
    # - Update the name.
    # - If a recipe ends up with duplicate ingredient names, we leave them (or we could try to merge).
    # Let's just update the names for now.
    
    # Better approach for SQL:
    # UPDATE ingredients SET name = :target_name WHERE name IN :source_names
    
    try:
        count = 0
        # 1. Find all ingredients that need to be renamed
        # We fetch them first to handle per-recipe logic
        ingredients_to_update = db.query(models.Ingredient).filter(models.Ingredient.name.in_(request.source_names)).all()
        
        for ing in ingredients_to_update:
            # Check if the recipe already has an ingredient with the target name
            existing_target = db.query(models.Ingredient).filter(
                models.Ingredient.recipe_id == ing.recipe_id,
                models.Ingredient.name == request.target_name
            ).first()
            
            if existing_target:
                # Case: Recipe has both "Tomate" (target) and "Tomates" (source)
                # We should merge them.
                # Strategy: Append quantity from source to target (e.g. "100g + 2 pieces")
                # and delete the source ingredient.
                if ing.quantity:
                    if existing_target.quantity:
                        existing_target.quantity = f"{existing_target.quantity} + {ing.quantity}"
                    else:
                        existing_target.quantity = ing.quantity
                
                db.delete(ing)
                count += 1
            else:
                # Case: Recipe only has "Tomates" (source)
                # Just rename it to "Tomate"
                ing.name = request.target_name
                count += 1
        
        db.commit()
        return {"message": f"Processed {count} ingredient records. Merged duplicates where necessary."}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ingredients/suggest-duplicates")
def suggest_duplicates(db: Session = Depends(database.get_db)):
    """
    Uses LLM to suggest duplicate ingredients to merge.
    """
    # 1. Get all distinct ingredient names
    all_names = crud.get_all_ingredients(db)
    
    # 2. Call LLM service
    suggestions = services.suggest_ingredient_duplicates(all_names)
    
    return {"suggestions": suggestions}
