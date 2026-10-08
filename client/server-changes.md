# Backend changes for pagination

`server/main.py`:

1. `/api/recipes` now accepts `offset`.
2. `total` is calculated before pagination.
3. Results are deduplicated by recipe ID.
4. The default "all recipes" pool is built from all TheMealDB categories instead of only six categories.
5. The response is sliced with `offset:offset + limit`.

Example:

```http
GET /api/recipes?limit=24&offset=0
GET /api/recipes?limit=24&offset=24
```
