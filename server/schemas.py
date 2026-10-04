from typing import Optional
from pydantic import BaseModel, Field


class IngredientIn(BaseModel):
    name: str
    measure: str = "по вкусу"


class RecipeOut(BaseModel):
    id: str
    title: str
    cuisine: str
    type: str
    time: Optional[int] = None
    kcal: Optional[int] = None
    difficulty: Optional[str] = None
    tags: list[str]
    image: str
    missing: int
    ingredients: list[str]
    measures: list[str] = []
    description: str
    instructions: str = ""
    source: str = ""
    youtube: str = ""


class RecipeListOut(BaseModel):
    items: list[RecipeOut]
    total: int


class FilterMeta(BaseModel):
    cuisines: list[str]
    types: list[str]
    ingredients: list[str]
    difficulties: list[str]
    time_options: list[int]


class HealthOut(BaseModel):
    status: str
    upstream: str