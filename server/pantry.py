from mapper import to_client_recipe


def enrich_with_pantry(meals: list[dict], pantry: list[str]) -> list[dict]:
    pantry_set = {p.strip().lower() for p in pantry if p and p.strip()}
    return [to_client_recipe(m, pantry_set) for m in meals]


def filter_only_available(recipes: list[dict]) -> list[dict]:
    return [r for r in recipes if r["missing"] == 0]