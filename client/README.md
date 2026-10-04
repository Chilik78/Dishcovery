# Dishcovery — Next.js client

## Run

```bash
npm install
cp .env.example .env.local
npm run dev
```

Default API:

```env
NEXT_PUBLIC_API_URL=http://localhost:8001/api
```

## Pagination / infinite scroll

The client requests recipes in pages of 24 using `offset` and automatically loads the next page when the scroll sentinel approaches the viewport.

The API contract is:

```http
GET /api/recipes?limit=24&offset=0
GET /api/recipes?limit=24&offset=24
GET /api/recipes?limit=24&offset=48
```

`total` is the number of unique recipes matching the active filters.
