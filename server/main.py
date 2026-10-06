from typing import Optional
import asyncio
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from schemas import RecipeOut, RecipeListOut, FilterMeta, HealthOut
from mealdb import (
    search_by_name, filter_by_area, filter_by_category,
    filter_by_ingredient, lookup_by_id, list_areas, list_categories,
    list_ingredients, random_meal, MealDBError,
)
from mapper import to_client_recipe, AREA_MAP, CATEGORY_MAP
from pantry import enrich_with_pantry, filter_only_available

app = FastAPI(
    title="Dishcovery API",
    description="Бэкенд для кулинарного приложения Dishcovery на TheMealDB",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _parse_pantry(pantry: Optional[str]) -> list[str]:
    if not pantry:
        return []
    return [p.strip() for p in pantry.split(",") if p.strip()]


def _area_en(cuisine: str) -> str:
    return next((en for en, ru in AREA_MAP.items() if ru == cuisine), cuisine)


def _categories_for_type(dish_type: str, all_categories: list[str]) -> list[str]:
    """Возвращает все категории TheMealDB, которые соответствуют типу UI.

    Например, UI-тип «Ужин» соответствует Beef, Chicken, Lamb, Pasta и т.д.
    """
    return [cat for cat in all_categories if CATEGORY_MAP.get(cat, cat) == dish_type or cat == dish_type]


async def _dedupe_refs(meals: list[dict]) -> list[dict]:
    unique: dict[str, dict] = {}
    for meal in meals:
        meal_id = str(meal.get("idMeal") or meal.get("id") or meal.get("strMeal") or "")
        if meal_id and meal_id not in unique:
            unique[meal_id] = meal
    return list(unique.values())


async def _collect_meals(
    q: Optional[str],
    cuisine: Optional[str],
    dish_type: Optional[str],
    ingredient: Optional[str],
) -> list[dict]:
    """Собирает кандидатов с применением ВСЕХ активных фильтров.

    TheMealDB предоставляет отдельные filter endpoints, поэтому комбинации
    фильтров реализуем пересечением множеств idMeal. Если задан q, сначала
    получаем результаты поиска, затем ограничиваем их остальными фильтрами.
    """
    all_categories = await list_categories()

    # Базовый набор кандидатов.
    if q:
        candidates = await search_by_name(q)
    elif cuisine:
        candidates = await filter_by_area(_area_en(cuisine))
    elif dish_type:
        cats = _categories_for_type(dish_type, all_categories)
        groups = await asyncio.gather(*(filter_by_category(cat) for cat in cats))
        candidates = [meal for group in groups for meal in group]
    elif ingredient:
        candidates = await filter_by_ingredient(ingredient)
    else:
        groups = await asyncio.gather(*(filter_by_category(cat) for cat in all_categories))
        candidates = [meal for group in groups for meal in group]

    candidates = await _dedupe_refs(candidates)

    # Дальше каждый дополнительный фильтр ограничивает текущий набор.
    # Работаем через idMeal, поэтому можно корректно комбинировать условия.
    candidate_ids = {
        str(m.get("idMeal") or m.get("id") or "") for m in candidates
    }

    if cuisine:
        area_meals = await filter_by_area(_area_en(cuisine))
        area_ids = {str(m.get("idMeal") or m.get("id") or "") for m in area_meals}
        candidate_ids &= area_ids

    if dish_type:
        cats = _categories_for_type(dish_type, all_categories)
        groups = await asyncio.gather(*(filter_by_category(cat) for cat in cats))
        type_ids = {
            str(m.get("idMeal") or m.get("id") or "")
            for group in groups for m in group
        }
        candidate_ids &= type_ids

    if ingredient:
        ing_meals = await filter_by_ingredient(ingredient)
        ing_ids = {str(m.get("idMeal") or m.get("id") or "") for m in ing_meals}
        candidate_ids &= ing_ids

    return [m for m in candidates if str(m.get("idMeal") or m.get("id") or "") in candidate_ids]


async def _load_full_meals(meals: list[dict]) -> list[dict]:
    """Добирает полные карточки рецептов для summary-ответов TheMealDB."""
    full: list[dict] = []
    tasks = []
    positions = []
    for idx, meal in enumerate(meals):
        if meal.get("strIngredient1") is not None or meal.get("strInstructions") is not None:
            full.append(meal)
            continue
        meal_id = str(meal.get("idMeal") or meal.get("id") or "")
        if meal_id:
            tasks.append(lookup_by_id(meal_id))
            positions.append(idx)
        else:
            full.append(meal)

    if tasks:
        details = await asyncio.gather(*tasks)
        full.extend(m for m in details if m)

    # lookup results are intentionally returned in provider order; duplicates
    # are removed later by the API endpoint.
    return full


def _apply_client_filters(recipes: list[dict], max_time: Optional[int],
                          diet: Optional[str], difficulty: Optional[str]) -> list[dict]:
    # TheMealDB does not provide real time/calories/difficulty.
    if diet and diet != "Все":
        d = diet.lower()
        recipes = [r for r in recipes if any(d in t.lower() for t in r.get("tags", []))]
    if max_time is not None:
        recipes = [r for r in recipes if r.get("time") is not None and r["time"] <= max_time]
    if difficulty and difficulty not in ("Любая", None):
        recipes = [r for r in recipes if r.get("difficulty") == difficulty]
    return recipes


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
    areas = await list_areas()
    cats = await list_categories()
    ings = await list_ingredients()
    return {
        "cuisines": ["Все кухни"] + list(dict.fromkeys(AREA_MAP.get(a, a) for a in areas)),
        "types": sorted(set(CATEGORY_MAP.get(c, c) for c in cats)),
        "ingredients": list(dict.fromkeys(ings)),
        "difficulties": [],
        "time_options": [],
    }


@app.get("/api/pantry/ingredients")
async def pantry_ingredients():
    return {"items": await list_ingredients()}


@app.get("/api/recipes", response_model=RecipeListOut)
async def list_recipes(
    q: Optional[str] = Query(None),
    cuisine: Optional[str] = Query(None),
    dish_type: Optional[str] = Query(None, alias="type"),
    ingredient: Optional[str] = Query(None),
    max_time: Optional[int] = Query(None, ge=1, le=240),
    diet: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    only_pantry: bool = Query(False),
    pantry: Optional[str] = Query(None),
    limit: int = Query(24, ge=1, le=60),
    offset: int = Query(0, ge=0),
):
    try:
        refs = await _collect_meals(q, cuisine, dish_type, ingredient)
        refs = await _dedupe_refs(refs)

        pantry_list = _parse_pantry(pantry)

        # Pantry mode needs ingredients of every candidate to calculate missing
        # and only_pantry correctly. Without it, load details only for this page.
        if only_pantry and pantry_list:
            raw = await _load_full_meals(refs)
            recipes = enrich_with_pantry(raw, pantry_list)
            recipes = filter_only_available(recipes)
            recipes = _apply_client_filters(recipes, max_time, diet, difficulty)
            unique: dict[str, dict] = {str(r["id"]): r for r in recipes}
            recipes = list(unique.values())
            total = len(recipes)
            page = recipes[offset:offset + limit]
            return {"items": page, "total": total}

        # Total of the recipe candidate pool is known before loading details.
        total = len(refs)
        page_refs = refs[offset:offset + limit]
        raw = await _load_full_meals(page_refs)
        recipes = enrich_with_pantry(raw, pantry_list) if pantry_list else [to_client_recipe(m) for m in raw]
        recipes = _apply_client_filters(recipes, max_time, diet, difficulty)
        return {"items": recipes, "total": total}

    except MealDBError as e:
        raise HTTPException(502, f"Upstream error: {e}")


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
