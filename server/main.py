from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from schemas import RecipeOut, RecipeListOut, FilterMeta, HealthOut
from mealdb import (
    search_by_name, filter_by_area, filter_by_category,
    lookup_by_id, list_areas, list_categories, list_ingredients,
    filter_by_ingredient,
    random_meal, MealDBError,
)
from mapper import to_client_recipe, AREA_MAP, CATEGORY_MAP
from pantry import enrich_with_pantry, filter_only_available

app = FastAPI(
    title="Dishcovery API",
    description="Бэкенд для кулинарного приложения Dishcovery на TheMealDB",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- helpers ----------

def _parse_pantry(pantry: Optional[str]) -> list[str]:
    if not pantry:
        return []
    return [p.strip() for p in pantry.split(",") if p.strip()]


async def _collect_meals(
    q: Optional[str],
    cuisine: Optional[str],
    dish_type: Optional[str],
    ingredient: Optional[str],
) -> list[dict]:
    """Собираем пул рецептов из TheMealDB в зависимости от фильтров."""
    if q:
        return await search_by_name(q)
    if ingredient:
        return await filter_by_ingredient(ingredient)
    if cuisine:
        area_en = next((en for en, ru in AREA_MAP.items() if ru == cuisine), cuisine)
        return await filter_by_area(area_en)
    if dish_type:
        cat_en = next((en for en, ru in CATEGORY_MAP.items() if ru == dish_type), dish_type)
        return await filter_by_category(cat_en)
    # Default: collect all categories exposed by TheMealDB.
    # The upstream API has no pagination, so our endpoint paginates the
    # resulting pool after deduplication.
    categories = await list_categories()
    results: list[dict] = []
    for cat in categories:
        results.extend(await filter_by_category(cat))
    return results


def _apply_client_filters(recipes: list[dict], max_time: Optional[int],
                          diet: Optional[str], difficulty: Optional[str]) -> list[dict]:
    """Apply only filters backed by real upstream data.

    TheMealDB does not provide preparation time, calories or difficulty, so
    those values must not be fabricated or used for filtering.
    """
    if diet and diet != "Все":
        d = diet.lower()
        recipes = [r for r in recipes if any(d in t.lower() for t in r.get("tags", []))]

    if max_time is not None:
        recipes = [r for r in recipes if r.get("time") is not None and r["time"] <= max_time]

    if difficulty and difficulty not in ("Любая", None):
        recipes = [r for r in recipes if r.get("difficulty") == difficulty]

    return recipes


# ---------- endpoints ----------

@app.get("/api/health", response_model=HealthOut)
async def health():
    try:
        await list_categories()
        upstream = "ok"
    except MealDBError:
        upstream = "unreachable"
    return {"status": "ok", "upstream": upstream}


@app.get("/api/meta", response_model=FilterMeta)
async def meta():
    """Справочники для панели фильтров клиента."""
    areas = await list_areas()
    cats = await list_categories()
    ings = await list_ingredients()
    return {
        "cuisines": ["Все кухни"] + [AREA_MAP.get(a, a) for a in areas],
        "types": sorted({CATEGORY_MAP.get(c, c) for c in cats}),
        "ingredients": ings,
        # TheMealDB does not provide real preparation time or difficulty.
        # Keep these lists empty until a real provider is integrated.
        "difficulties": [],
        "time_options": [],
    }


@app.get("/api/pantry/ingredients")
async def pantry_ingredients():
    """Список ингредиентов для модалки «Что есть дома?»."""
    ings = await list_ingredients()
    return {"items": ings}


@app.get("/api/recipes", response_model=RecipeListOut)
async def list_recipes(
    q: Optional[str] = Query(None, description="Поиск по названию/ингредиенту"),
    cuisine: Optional[str] = Query(None),
    dish_type: Optional[str] = Query(None, alias="type"),
    ingredient: Optional[str] = Query(None),
    max_time: Optional[int] = Query(None, ge=1, le=240),
    diet: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    only_pantry: bool = Query(False),
    pantry: Optional[str] = Query(None, description="CSV: 'Яйца,Томаты,Паста'"),
    limit: int = Query(24, ge=1, le=60),
    offset: int = Query(0, ge=0),
):
    try:
        raw = await _collect_meals(q, cuisine, dish_type, ingredient)
    except MealDBError as e:
        raise HTTPException(502, f"Upstream error: {e}")

    pantry_list = _parse_pantry(pantry)
    recipes = enrich_with_pantry(raw, pantry_list) if pantry_list else [to_client_recipe(m) for m in raw]

    recipes = _apply_client_filters(recipes, max_time, diet, difficulty)

    if only_pantry:
        recipes = filter_only_available(recipes)

    # TheMealDB does not provide pagination. Build the complete filtered pool
    # first, remove duplicates, then paginate our API response.
    unique: dict[str, dict] = {}
    for recipe in recipes:
        unique[str(recipe.get("id", ""))] = recipe
    recipes = list(unique.values())

    total = len(recipes)
    recipes = recipes[offset:offset + limit]
    return {"items": recipes, "total": total}


@app.get("/api/recipes/random", response_model=RecipeOut)
async def recipe_random():
    meal = await random_meal()
    if not meal:
        raise HTTPException(404, "No random meal")
    return to_client_recipe(meal)


@app.get("/api/recipes/{recipe_id}", response_model=RecipeOut)
async def recipe_detail(recipe_id: str):
    meal = await lookup_by_id(recipe_id)
    if not meal:
        raise HTTPException(404, "Recipe not found")
    return to_client_recipe(meal)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")