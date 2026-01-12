from sqlalchemy import Column, Integer, String, ForeignKey, Float, Text, Table, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

meal_plan_recipes = Table(
    'meal_plan_recipes',
    Base.metadata,
    Column('meal_plan_id', Integer, ForeignKey('meal_plans.id')),
    Column('recipe_id', Integer, ForeignKey('recipes.id'))
)

recipe_tags = Table(
    'recipe_tags',
    Base.metadata,
    Column('recipe_id', Integer, ForeignKey('recipes.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

class MealPlan(Base):
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    recipes = relationship("Recipe", secondary=meal_plan_recipes, back_populates="meal_plans")

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    color = Column(String, default="#6366f1")

    recipes = relationship("Recipe", secondary=recipe_tags, back_populates="tags")

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    source_file = Column(String, nullable=True)

    ingredients = relationship("Ingredient", back_populates="recipe", cascade="all, delete-orphan")
    instructions = relationship("Instruction", back_populates="recipe", cascade="all, delete-orphan")
    meal_plans = relationship("MealPlan", secondary=meal_plan_recipes, back_populates="recipes")
    tags = relationship("Tag", secondary=recipe_tags, back_populates="recipes")

class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    quantity = Column(String) # Using string to handle units like "1 cup", "200g" easily for now, or could be split
    recipe_id = Column(Integer, ForeignKey("recipes.id"))

    recipe = relationship("Recipe", back_populates="ingredients")

class Instruction(Base):
    __tablename__ = "instructions"

    id = Column(Integer, primary_key=True, index=True)
    step_number = Column(Integer)
    text = Column(Text)
    recipe_id = Column(Integer, ForeignKey("recipes.id"))

    recipe = relationship("Recipe", back_populates="instructions")

class ImportTask(Base):
    __tablename__ = "import_tasks"

    id = Column(String, primary_key=True)  # UUID
    status = Column(String, index=True)  # pending, processing, completed, failed
    filename = Column(String, nullable=True)
    result = Column(Text, nullable=True)  # JSON string of recipe data
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class IngredientMigration(Base):
    """Tracks ingredient re-extraction migration progress for each recipe."""
    __tablename__ = "ingredient_migrations"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), index=True)
    status = Column(String, index=True)  # pending, processing, completed, failed, skipped
    original_count = Column(Integer)  # Number of ingredients before migration
    new_count = Column(Integer, nullable=True)  # Number of ingredients after migration
    error = Column(Text, nullable=True)  # Error message if failed
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    recipe = relationship("Recipe")
