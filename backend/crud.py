from sqlalchemy.orm import Session
from sqlalchemy import or_, distinct
import models, schemas
from typing import List

def get_recipe(db: Session, recipe_id: int):
    return db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()

def get_recipes(db: Session, skip: int = 0, limit: int = 100, ingredients: List[str] = None, search: str = None, source_file: str = None):
    query = db.query(models.Recipe)

    if ingredients:
        # Filter recipes that contain ANY of the specified ingredients (OR logic)
        # Use JOIN instead of any() for better performance with the recipe_id index
        query = query.join(models.Ingredient).filter(
            or_(*[models.Ingredient.name.ilike(f"%{ing}%") for ing in ingredients])
        ).distinct()

    if search:
        query = query.filter(models.Recipe.name.ilike(f"%{search}%"))

    if source_file:
        query = query.filter(models.Recipe.source_file == source_file)

    return query.offset(skip).limit(limit).all()

def get_all_ingredients(db: Session):
    # Return distinct ingredient names as a list of strings
    results = db.query(models.Ingredient.name).distinct().all()
    return [row[0] for row in results]

def get_recipe_count(db: Session, ingredients: List[str] = None, search: str = None, source_file: str = None):
    query = db.query(models.Recipe)

    if ingredients:
        # Filter recipes that contain ANY of the specified ingredients (OR logic)
        # Use JOIN instead of any() for better performance with the recipe_id index
        query = query.join(models.Ingredient).filter(
            or_(*[models.Ingredient.name.ilike(f"%{ing}%") for ing in ingredients])
        ).distinct()

    if search:
        query = query.filter(models.Recipe.name.ilike(f"%{search}%"))

    if source_file:
        query = query.filter(models.Recipe.source_file == source_file)

    return query.count()

def create_recipe(db: Session, recipe: schemas.RecipeCreate):
    db_recipe = models.Recipe(name=recipe.name, description=recipe.description, source_file=recipe.source_file)
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)

    for ingredient in recipe.ingredients:
        db_ingredient = models.Ingredient(**ingredient.dict(), recipe_id=db_recipe.id)
        db.add(db_ingredient)

    for instruction in recipe.instructions:
        db_instruction = models.Instruction(**instruction.dict(), recipe_id=db_recipe.id)
        db.add(db_instruction)

    db.commit()
    db.refresh(db_recipe)
    return db_recipe

def delete_recipe(db: Session, recipe_id: int):
    db_recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if db_recipe:
        db.delete(db_recipe)
        db.commit()
    return db_recipe

def create_meal_plan(db: Session, meal_plan: schemas.MealPlanCreate):
    db_meal_plan = models.MealPlan(name=meal_plan.name)

    # Fetch recipes
    recipes = db.query(models.Recipe).filter(models.Recipe.id.in_(meal_plan.recipe_ids)).all()
    db_meal_plan.recipes = recipes

    db.add(db_meal_plan)
    db.commit()
    db.refresh(db_meal_plan)
    return db_meal_plan

def get_meal_plans(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.MealPlan).offset(skip).limit(limit).all()

def get_meal_plan(db: Session, meal_plan_id: int):
    return db.query(models.MealPlan).filter(models.MealPlan.id == meal_plan_id).first()

def delete_meal_plan(db: Session, meal_plan_id: int):
    db_meal_plan = db.query(models.MealPlan).filter(models.MealPlan.id == meal_plan_id).first()
    if db_meal_plan:
        db.delete(db_meal_plan)
        db.commit()
        return True
    return False

def update_recipe(db: Session, recipe_id: int, recipe: schemas.RecipeCreate):
    db_recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not db_recipe:
        return None

    db_recipe.name = recipe.name
    db_recipe.description = recipe.description

    # Clear existing ingredients and instructions (simple approach)
    # In a real app you might want to update/diff them
    db.query(models.Ingredient).filter(models.Ingredient.recipe_id == recipe_id).delete()
    db.query(models.Instruction).filter(models.Instruction.recipe_id == recipe_id).delete()

    for ingredient in recipe.ingredients:
        db_ingredient = models.Ingredient(**ingredient.dict(), recipe_id=db_recipe.id)
        db.add(db_ingredient)

    for instruction in recipe.instructions:
        db_instruction = models.Instruction(**instruction.dict(), recipe_id=db_recipe.id)
        db.add(db_instruction)

    db.commit()
    db.refresh(db_recipe)
    return db_recipe
