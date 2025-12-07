from pydantic import BaseModel
from typing import List, Optional, Union
from datetime import datetime

class IngredientBase(BaseModel):
    name: str
    quantity: str

class IngredientCreate(IngredientBase):
    pass

class Ingredient(IngredientBase):
    id: int
    recipe_id: int

    class Config:
        orm_mode = True

class InstructionBase(BaseModel):
    step_number: int
    text: str

class InstructionCreate(InstructionBase):
    pass

class Instruction(InstructionBase):
    id: int
    recipe_id: int

    class Config:
        orm_mode = True

class TagBase(BaseModel):
    name: str
    color: Optional[str] = "#6366f1"

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int

    class Config:
        orm_mode = True

class RecipeBase(BaseModel):
    name: str
    description: Optional[str] = None
    source_file: Optional[str] = None

class RecipeCreate(RecipeBase):
    ingredients: List[IngredientCreate]
    instructions: List[InstructionCreate]
    tags: List[Union[str, TagCreate]] = []

class Recipe(RecipeBase):
    id: int
    ingredients: List[Ingredient] = []
    instructions: List[Instruction] = []
    tags: List[Tag] = []

    class Config:
        orm_mode = True

class MealPlanBase(BaseModel):
    name: str

class MealPlanCreate(MealPlanBase):
    recipe_ids: List[int]

class MealPlan(MealPlanBase):
    id: int
    created_at: datetime
    recipes: List[Recipe] = []

    class Config:
        orm_mode = True

class RecipeSearchRequest(BaseModel):
    ingredients: List[str]
    provider: Optional[str] = "gemini"
