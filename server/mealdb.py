import httpx
from typing import Any
from config import settings
from cache import cache_get, cache_set


class MealDBError(Exception):
    pass


async def _get(path: str, params: dict | None = None) -> dict[str, Any]:
    url = f"{settings.mealdb_base_url}/{path}"
    params = params or {}
    if settings.mealdb_api_key and settings.mealdb_api_key != "1":
        params["apiKey"] = settings.mealdb_api_key

    cache_key = f"{path}:{sorted(params.items())}"
    if (cached := cache_get(cache_key)) is not None:
        return cached

    async with httpx.AsyncClient(timeout=settings.http_timeout) as client:
        try:
            r = await client.get(url, params=params)
            r.raise_for_status()
        except httpx.HTTPError as e:
            raise MealDBError(str(e)) from e

    data = r.json()
    cache_set(cache_key, data)
    return data


async def search_by_name(query: str) -> list[dict]:
    data = await _get("search.php", {"s": query})
    return data.get("meals") or []


async def filter_by_ingredient(ingredient: str) -> list[dict]:
    data = await _get("filter.php", {"i": ingredient})
    return data.get("meals") or []


async def filter_by_area(area: str) -> list[dict]:
    data = await _get("filter.php", {"a": area})
    return data.get("meals") or []


async def filter_by_category(category: str) -> list[dict]:
    data = await _get("filter.php", {"c": category})
    return data.get("meals") or []


async def lookup_by_id(meal_id: str) -> dict | None:
    data = await _get("lookup.php", {"i": meal_id})
    meals = data.get("meals") or []
    return meals[0] if meals else None


async def list_areas() -> list[str]:
    data = await _get("list.php", {"a": "list"})
    return [m["strArea"] for m in (data.get("meals") or []) if m.get("strArea")]


async def list_categories() -> list[str]:
    data = await _get("list.php", {"c": "list"})
    return [m["strCategory"] for m in (data.get("meals") or []) if m.get("strCategory")]


async def list_ingredients() -> list[str]:
    data = await _get("list.php", {"i": "list"})
    return [m["strIngredient"] for m in (data.get("meals") or []) if m.get("strIngredient")]


async def random_meal() -> dict | None:
    data = await _get("random.php")
    meals = data.get("meals") or []
    return meals[0] if meals else None