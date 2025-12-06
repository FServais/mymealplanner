from sqlalchemy.orm import Session
from sqlalchemy import or_, distinct
import models, schemas
from typing import List

def get_recipe(db: Session, recipe_id: int):
    return db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()

def get_recipes(db: Session, skip: int = 0, limit: int = 100, ingredients: List[str] = None, tags: List[str] = None, search: str = None, source_file: str = None):
    query = db.query(models.Recipe)

    if ingredients:
        # Filter recipes that contain ANY of the specified ingredients (OR logic)
        # Use JOIN instead of any() for better performance with the recipe_id index
        query = query.join(models.Ingredient).filter(
            or_(*[models.Ingredient.name.ilike(f"%{ing}%") for ing in ingredients])
        ).distinct()

    if tags:
        # Filter recipes that contain ANY of the specified tags (OR logic)
        query = query.join(models.Recipe.tags).filter(
            models.Tag.name.in_(tags)
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

def get_all_tags(db: Session):
    # Return all tags
    return db.query(models.Tag).all()

def create_tag(db: Session, tag: schemas.TagCreate):
    db_tag = models.Tag(name=tag.name, color=tag.color)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

def update_tag(db: Session, tag_id: int, tag: schemas.TagCreate):
    db_tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if db_tag:
        db_tag.name = tag.name
        db_tag.color = tag.color
        db.commit()
        db.refresh(db_tag)
    return db_tag

def delete_tag(db: Session, tag_id: int):
    db_tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if db_tag:
        db.delete(db_tag)
        db.commit()
        return True
    return False

def get_recipe_count(db: Session, ingredients: List[str] = None, tags: List[str] = None, search: str = None, source_file: str = None):
    query = db.query(models.Recipe)

    if ingredients:
        # Filter recipes that contain ANY of the specified ingredients (OR logic)
        # Use JOIN instead of any() for better performance with the recipe_id index
        query = query.join(models.Ingredient).filter(
            or_(*[models.Ingredient.name.ilike(f"%{ing}%") for ing in ingredients])
        ).distinct()

    if tags:
        # Filter recipes that contain ANY of the specified tags (OR logic)
        query = query.join(models.Recipe.tags).filter(
            models.Tag.name.in_(tags)
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

    # Handle tags
    for tag_input in recipe.tags:
        tag_name = tag_input
        tag_color = "#6366f1"
        
        if hasattr(tag_input, 'name'):
             tag_name = tag_input.name
             tag_color = tag_input.color

        # Check if tag exists
        db_tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
        if not db_tag:
            db_tag = models.Tag(name=tag_name, color=tag_color)
            db.add(db_tag)
        else:
            # Update color if provided and different? 
            # Let's say we update it if it's explicitly passed object
            if hasattr(tag_input, 'color'):
                db_tag.color = tag_color
                
        db_recipe.tags.append(db_tag)

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

    # Update tags
    db_recipe.tags = [] # Clear existing associations
    for tag_input in recipe.tags:
        tag_name = tag_input
        tag_color = "#6366f1"
        
        if hasattr(tag_input, 'name'):
             tag_name = tag_input.name
             tag_color = tag_input.color

        db_tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
        if not db_tag:
            db_tag = models.Tag(name=tag_name, color=tag_color)
            db.add(db_tag)
        else:
             if hasattr(tag_input, 'color'):
                db_tag.color = tag_color

        db_recipe.tags.append(db_tag)
    
    db.commit()
    db.refresh(db_recipe)
    return db_recipe
