import re
from typing import Any

# ---------- Локализация ----------

AREA_MAP = {
    "Italian": "Итальянская",
    "Japanese": "Японская",
    "Chinese": "Китайская",
    "Thai": "Тайская",
    "Indian": "Индийская",
    "Mexican": "Мексиканская",
    "French": "Французская",
    "Greek": "Греческая",
    "Spanish": "Испанская",
    "Moroccan": "Марокканская",
    "Turkish": "Турецкая",
    "American": "Американская",
    "British": "Британская",
    "Canadian": "Канадская",
    "Egyptian": "Египетская",
    "Irish": "Ирландская",
    "Jamaican": "Ямайская",
    "Kenyan": "Кенийская",
    "Malaysian": "Малайзийская",
    "Polish": "Польская",
    "Portuguese": "Португальская",
    "Russian": "Русская",
    "Saudi Arabian": "Саудовская",
    "Tunisian": "Тунисская",
    "Ukrainian": "Украинская",
    "Uruguayan": "Уругвайская",
    "Vietnamese": "Вьетнамская",
    "Dutch": "Нидерландская",
    "Croatian": "Хорватская",
    "Filipino": "Филиппинская",
    "Norwegian": "Норвежская",
    "Syrian": "Сирийская",
    "Algerian": "Алжирская",
    "Argentinian": "Аргентинская",
    "Australian": "Австралийская",
    "Venezulan": "Венесуэльская",
    "Unknown": "Авторская",
}

CATEGORY_MAP = {
    "Beef": "Ужин",
    "Chicken": "Ужин",
    "Dessert": "Десерт",
    "Lamb": "Ужин",
    "Miscellaneous": "Ужин",
    "Pasta": "Ужин",
    "Pork": "Ужин",
    "Seafood": "Ужин",
    "Side": "Гарнир",
    "Starter": "Закуска",
    "Vegan": "Ужин",
    "Vegetarian": "Ужин",
    "Breakfast": "Завтрак",
    "Goat": "Ужин",
}

# Теги-диеты/темы, которые клиент ищет подстрокой
TAG_KEYWORDS = {
    "Vegan": "Веган",
    "Vegetarian": "Вегетарианское",
    "Gluten": "Без глютена",       # упрощённо
    "Dairy": "Без лактозы",        # упрощённо
    "Pescatarian": "Пескетарианское",
    "Keto": "Кето",
    "Low": "Лёгкое",
    "Spicy": "Острое",
    "Quick": "Быстро",
    "Comfort": "Уютная еда",
    "High": "Высокий белок",
}


def _extract_ingredients(meal: dict[str, Any]) -> tuple[list[str], list[str]]:
    names: list[str] = []
    measures: list[str] = []
    for i in range(1, 21):
        name = (meal.get(f"strIngredient{i}") or "").strip()
        measure = (meal.get(f"strMeasure{i}") or "").strip()
        if name:
            names.append(name)
            measures.append(measure or "по вкусу")
    return names, measures


def _extract_tags(meal: dict[str, Any]) -> list[str]:
    raw = (meal.get("strTags") or "").split(",")
    tags: list[str] = []
    for t in raw:
        t = t.strip()
        if not t:
            continue
        for key, localized in TAG_KEYWORDS.items():
            if key.lower() in t.lower():
                tags.append(localized)
                break
        else:
            tags.append(t)
    # добавляем тип блюда как тег для фильтра
    cat = meal.get("strCategory")
    if cat in ("Vegan", "Vegetarian"):
        tags.append("Вегетарианское" if cat == "Vegetarian" else "Веган")
    return list(dict.fromkeys(tags))  # dedupe с сохранением порядка


def _safe_id(meal: dict) -> str:
    return str(meal.get("idMeal") or meal.get("strMeal") or "unknown")


def to_client_recipe(meal: dict[str, Any], pantry: set[str] | None = None) -> dict[str, Any]:
    """Превращает ответ TheMealDB в объект, который ждёт React-клиент."""
    meal_id = _safe_id(meal)
    ingredients, measures = _extract_ingredients(meal)
    tags = _extract_tags(meal)

    area = meal.get("strArea") or "Unknown"
    cuisine = AREA_MAP.get(area, area)
    category = meal.get("strCategory") or "Miscellaneous"
    dish_type = CATEGORY_MAP.get(category, "Ужин")

    missing = 0
    if pantry is not None:
        pantry_lower = {p.lower() for p in pantry}
        missing = sum(
            1 for ing in ingredients
            if ing.lower() not in pantry_lower
            and not any(p in ing.lower() for p in pantry_lower)
        )

    return {
        "id": meal_id,
        "title": meal.get("strMeal") or "Без названия",
        "cuisine": cuisine,
        "type": dish_type,
        # TheMealDB does not expose preparation time, calories or difficulty.
        # Do not synthesize these values; return null until a real nutrition/time
        # provider is integrated.
        "time": None,
        "kcal": None,
        "difficulty": None,
        "tags": tags,
        "image": meal.get("strMealThumb") or "",
        "missing": missing,
        "ingredients": ingredients,
        "measures": measures,
        "description": (meal.get("strInstructions") or "").split(".")[0].strip()[:160]
                       or f"{dish_type} в стиле «{cuisine}».",
        # доп. поля — не мешают клиенту
        "instructions": meal.get("strInstructions") or "",
        "source": meal.get("strSource") or "",
        "youtube": meal.get("strYoutube") or "",
    }