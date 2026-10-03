# Dishcovery

Адаптивный React-интерфейс для сервиса рецептов Dishcovery. В проекте уже есть:
- персональная лента рецептов;
- поиск по названию и ингредиентам;
- фильтры по кухне, времени, диете и сложности;
- «что есть в холодильнике» с режимом «Готово прямо сейчас»;
- сохранение рецептов;
- детальная страница рецепта;
- пошаговое приготовление с прогрессом и таймером;
- mobile-first responsive layout;
- подготовленная переменная `VITE_API_URL` для FastAPI.

## Запуск

```bash
npm install
npm run dev
```

## Подключение FastAPI

Создайте `.env`:

```env
VITE_API_URL=http://localhost:8000/api
```

Далее замените demo-массив `recipes` в `src/main.jsx` на запрос к API.

Рекомендуемый контракт:

`GET /api/recipes?query=&max_time=30&cuisine=&diet=&difficulty=&ingredients=tomato,egg`

Ответ:

```json
{
  "items": [
    {
      "id": 1,
      "title": "Паста...",
      "description": "...",
      "image": "...",
      "cuisine": "Итальянская",
      "type": "Ужин",
      "time": 20,
      "kcal": 520,
      "difficulty": "Новичок",
      "tags": ["Вегетарианское"],
      "ingredients": ["Паста", "Томаты"]
    }
  ],
  "total": 1
}
```

Для production желательно вынести API-клиент в `src/api/recipes.js`, а состояние фильтров — в отдельный hook/store.
