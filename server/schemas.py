from typing import Annotated, Optional
from pydantic import BaseModel, Field, StringConstraints


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


class RecipeStepsOut(BaseModel):
    steps: list[Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]] = Field(
        min_length=1,
        max_length=20,
        description="Порядок приготовления на русском языке. Каждый элемент списка — отдельный шаг.",
        examples=[["Нарежьте чеснок.", "Обжарьте его на растительном масле 2 минуты."]],
    )


class RecipeStepsErrorOut(BaseModel):
    detail: str


class FilterMeta(BaseModel):
    cuisines: list[str]
    types: list[str]
    ingredients: list[str]
    difficulties: list[str]
    time_options: list[int]


class HealthOut(BaseModel):
    status: str
    upstream: str
