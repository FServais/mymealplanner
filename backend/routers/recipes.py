from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import crud
import models
import schemas
import database
import services

router = APIRouter(
    prefix="/recipes",
    tags=["recipes"],
)

@router.post("/", response_model=schemas.Recipe)
def create_recipe(recipe: schemas.RecipeCreate, db: Session = Depends(database.get_db)):
    return crud.create_recipe(db=db, recipe=recipe)

@router.get("/", response_model=List[schemas.Recipe])
def read_recipes(
    skip: int = 0,
    limit: int = 100,
    ingredients: List[str] = Query(None),
    search: Optional[str] = None,
    source_file: Optional[str] = None,
    db: Session = Depends(database.get_db)
):
    recipes = crud.get_recipes(db, skip=skip, limit=limit, ingredients=ingredients, search=search, source_file=source_file)
    return recipes

@router.get("/ingredients", response_model=List[str])
@router.get("/ingredients", response_model=List[str])
def read_ingredients(db: Session = Depends(database.get_db)):
    return crud.get_all_ingredients(db)

@router.get("/count")
def read_recipe_count(
    ingredients: List[str] = Query(None),
    search: Optional[str] = None,
    source_file: Optional[str] = None,
    db: Session = Depends(database.get_db)
):
    count = crud.get_recipe_count(db, ingredients=ingredients, search=search, source_file=source_file)
    return {"count": count}

@router.get("/{recipe_id}", response_model=schemas.Recipe)
def read_recipe(recipe_id: int, db: Session = Depends(database.get_db)):
    db_recipe = crud.get_recipe(db, recipe_id=recipe_id)
    if db_recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return db_recipe

@router.put("/{recipe_id}", response_model=schemas.Recipe)
def update_recipe(recipe_id: int, recipe: schemas.RecipeCreate, db: Session = Depends(database.get_db)):
    db_recipe = crud.update_recipe(db, recipe_id=recipe_id, recipe=recipe)
    if db_recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return db_recipe

@router.delete("/{recipe_id}")
def delete_recipe(recipe_id: int, db: Session = Depends(database.get_db)):
    crud.delete_recipe(db, recipe_id=recipe_id)
    return {"ok": True}

@router.post("/import/pdf")
async def import_recipe_pdf(file: UploadFile = File(...)):
    content = await file.read()
    text = services.extract_text_from_pdf(content)
    if not text:
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")

    recipe_data = services.parse_recipe_with_llm(text)

    # Check if parsing resulted in an error
    if recipe_data.get("name", "").startswith("Error"):
        error_detail = recipe_data.get("description", "Unknown error occurred")
        raise HTTPException(status_code=500, detail=error_detail)

    recipe_data["source_file"] = file.filename
    return recipe_data
