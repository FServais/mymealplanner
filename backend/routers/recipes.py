import uuid
import json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, BackgroundTasks
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
    tags: List[str] = Query(None),
    search: Optional[str] = None,
    source_file: Optional[str] = None,
    db: Session = Depends(database.get_db)
):
    recipes = crud.get_recipes(db, skip=skip, limit=limit, ingredients=ingredients, tags=tags, search=search, source_file=source_file)
    return recipes

@router.get("/tags", response_model=List[schemas.Tag])
def read_tags(db: Session = Depends(database.get_db)):
    return crud.get_all_tags(db)

@router.post("/tags", response_model=schemas.Tag)
def create_tag(tag: schemas.TagCreate, db: Session = Depends(database.get_db)):
    # Check if exists
    existing = crud.get_all_tags(db)
    if any(t.name == tag.name for t in existing):
        raise HTTPException(status_code=400, detail="Tag already exists")
    return crud.create_tag(db, tag)

@router.put("/tags/{tag_id}", response_model=schemas.Tag)
def update_tag(tag_id: int, tag: schemas.TagCreate, db: Session = Depends(database.get_db)):
    db_tag = crud.update_tag(db, tag_id, tag)
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return db_tag

@router.delete("/tags/{tag_id}")
def delete_tag(tag_id: int, db: Session = Depends(database.get_db)):
    success = crud.delete_tag(db, tag_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tag not found")
    return {"ok": True}

@router.get("/ingredients", response_model=List[str])
def read_ingredients(db: Session = Depends(database.get_db)):
    return crud.get_all_ingredients(db)

@router.get("/source-files", response_model=List[str])
def get_source_files(db: Session = Depends(database.get_db)):
    """Get distinct source_file values for filtering PDF imports."""
    from sqlalchemy import distinct
    results = db.query(distinct(models.Recipe.source_file))\
                .filter(models.Recipe.source_file.isnot(None))\
                .filter(models.Recipe.source_file != "")\
                .order_by(models.Recipe.source_file)\
                .all()
    return [r[0] for r in results]

@router.get("/count")
def read_recipe_count(
    ingredients: List[str] = Query(None),
    tags: List[str] = Query(None),
    search: Optional[str] = None,
    source_file: Optional[str] = None,
    db: Session = Depends(database.get_db)
):
    count = crud.get_recipe_count(db, ingredients=ingredients, tags=tags, search=search, source_file=source_file)
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

@router.patch("/{recipe_id}/ingredients", response_model=schemas.Recipe)
def patch_recipe_ingredients(
    recipe_id: int,
    ingredients: List[schemas.IngredientCreate],
    db: Session = Depends(database.get_db)
):
    """Quick update of only ingredients for a recipe (for bulk review workflow)."""
    db_recipe = crud.get_recipe(db, recipe_id=recipe_id)
    if db_recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # Delete existing ingredients
    db.query(models.Ingredient).filter(models.Ingredient.recipe_id == recipe_id).delete()

    # Add new ingredients
    for ing in ingredients:
        db_ingredient = models.Ingredient(
            name=ing.name,
            quantity=ing.quantity,
            recipe_id=recipe_id
        )
        db.add(db_ingredient)

    db.commit()
    db.refresh(db_recipe)
    return db_recipe

@router.post("/import/pdf")
async def import_recipe_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    provider: str = Query("openai", description="LLM provider to use: 'openai' or 'gemini'"),
    db: Session = Depends(database.get_db)
):
    content = await file.read()

    # Validate provider
    provider = provider.lower().strip()
    if provider not in ["openai", "gemini"]:
        raise HTTPException(status_code=400, detail="Invalid provider. Use 'openai' or 'gemini'.")

    # Generate a unique task ID
    task_id = str(uuid.uuid4())

    # Create task in database
    import_task = models.ImportTask(
        id=task_id,
        status="pending",
        filename=file.filename
    )
    db.add(import_task)
    db.commit()

    # Start background task with provider
    background_tasks.add_task(
        services.process_pdf_import_task,
        task_id,
        content,
        file.filename,
        provider
    )

    return {"task_id": task_id, "status": "pending", "provider": provider}

@router.get("/import/status/{task_id}")
def get_import_status(task_id: str, db: Session = Depends(database.get_db)):
    task = db.query(models.ImportTask).filter(models.ImportTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    response = {
        "status": task.status,
        "created_at": task.created_at.isoformat() if task.created_at else None
    }
    
    if task.status == "completed" and task.result:
        response["result"] = json.loads(task.result)
    elif task.status == "failed" and task.error:
        response["error"] = task.error
    
    return response

@router.post("/search/ai", response_model=List[schemas.Recipe])
def search_recipes_ai(
    request: schemas.RecipeSearchRequest,
    db: Session = Depends(database.get_db)
):
    """
    Search for recipes using AI to find the best matches for the given ingredients.
    """
    # 1. Get recipes containing ANY of the ingredients (broad search)
    # We use the existing filter logic or direct query
    # To be efficient, we might want to get all recipes that match at least one ingredient
    # relying on the existing crud.get_recipes might be enough if we pass all ingredients
    
    # Using crud.get_recipes with ingredients list (OR logic)
    candidate_recipes = crud.get_recipes(db, ingredients=request.ingredients, limit=50) # Limit candidate pool
    
    if not candidate_recipes:
        return []

    # 2. Use AI to select top 5
    selected_ids = services.find_best_recipes(
        ingredients=request.ingredients,
        recipes=candidate_recipes,
        provider=request.provider
    )
    
    # 3. Return full recipe objects (preserving order from AI if possible, but SQL IN clause doesn't guarantee order)
    # So we fetch them and reorder in python
    
    if not selected_ids:
        return []
        
    final_recipes = db.query(models.Recipe).filter(models.Recipe.id.in_(selected_ids)).all()
    
    # Sort final_recipes based on the order of selected_ids
    id_map = {r.id: r for r in final_recipes}
    ordered_recipes = [id_map[id] for id in selected_ids if id in id_map]
    
    return ordered_recipes
