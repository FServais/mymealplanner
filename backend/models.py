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

class MealPlan(Base):
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    recipes = relationship("Recipe", secondary=meal_plan_recipes, back_populates="meal_plans")

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    source_file = Column(String, nullable=True)

    ingredients = relationship("Ingredient", back_populates="recipe", cascade="all, delete-orphan")
    instructions = relationship("Instruction", back_populates="recipe", cascade="all, delete-orphan")
    meal_plans = relationship("MealPlan", secondary=meal_plan_recipes, back_populates="recipes")

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
