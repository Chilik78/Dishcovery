# Dishcovery Client

Frontend-приложение Dishcovery на **Next.js + React + TypeScript**.

Клиент отвечает за интерфейс поиска рецептов, фильтрацию, Pantry Mode, карточки рецептов и автоматическую пагинацию.

## Стек

- Next.js 16;
- React;
- TypeScript;
- CSS;
- Fetch API;
- FastAPI как backend.

## Запуск

```bash
npm install
```

Создайте `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8001/api
```

Запуск development-сервера:

```bash
npm run dev
```

Откройте:

```text
http://localhost:3000
```

Production:

```bash
npm run build
npm run start
```

## Переменные окружения

### `NEXT_PUBLIC_API_URL`

URL REST API Dishcovery.

По умолчанию:

```env
NEXT_PUBLIC_API_URL=http://localhost:8001/api
```

При размещении frontend и backend на разных доменах укажите публичный URL FastAPI.

## Структура

```text
client/
├── src/
│   ├── app/
│   │   ├── page.tsx
│   │   ├── layout.tsx
│   │   └── recipe/
│   │       └── [id]/
│   │           └── page.tsx
│   │
│   ├── components/
│   │   ├── HomeClient.tsx
│   │   └── RecipeCard.tsx
│   │
│   └── lib/
│       └── api.ts
│
├── public/
├── .env.local
├── next.config.ts
├── tsconfig.json
└── package.json
```

## Работа с API

Все запросы к backend собраны в:

```text
src/lib/api.ts
```

Главные операции:

```text
api.meta()
api.recipes(...)
api.recipe(id)
api.random()
api.pantryIngredients()
```

Компоненты не обращаются напрямую к TheMealDB.

## Поиск

При вводе текста пользователь может выполнить поиск по названию.

Пример запроса:

```http
GET /api/recipes?q=pasta&limit=24&offset=0
```

Поиск выполняется только после отправки формы.

## Фильтры

Клиент передаёт активные фильтры в `/api/recipes`.

Например:

```http
GET /api/recipes
  ?q=chicken
  &cuisine=Итальянская
  &type=Ужин
  &ingredient=Garlic
  &limit=24
  &offset=0
```

Изменение активного фильтра сбрасывает pagination на:

```text
offset = 0
```

и загружает новую подборку.

## Pantry Mode

Для Pantry Mode используется двухэтапная модель.

### 1. Выбор

Пользователь отмечает ингредиенты.

На этом этапе запросы к серверу не выполняются.

Используется:

```text
pendingPantry
```

### 2. Применение

После нажатия кнопки ингредиенты переносятся в:

```text
pantry
```

и выполняется один API-запрос.

Это предотвращает серию запросов при выборе нескольких ингредиентов.

## Infinite Scroll

Рецепты загружаются страницами по 24 элемента.

```text
offset=0
offset=24
offset=48
offset=72
...
```

Для определения необходимости следующего запроса используется `IntersectionObserver`.

Когда специальный sentinel возле конца списка появляется в viewport, клиент загружает следующую страницу.

Повторяющиеся рецепты дополнительно удаляются по `recipe.id`.

## Состояния интерфейса

Клиент обрабатывает:

- загрузку первой страницы;
- загрузку следующей страницы;
- пустой результат;
- ошибку API;
- конец списка;
- сохранённые рецепты;
- активные фильтры.

## Saved Recipes

Избранные рецепты текущая версия хранит в `localStorage`.

Ключ:

```text
dishcovery:saved
```

Это локальное сохранение браузера, а не пользовательское хранилище на backend.

Для production-версии можно перенести избранное в PostgreSQL и привязать его к аккаунту пользователя.

## Важные правила разработки

Не добавляйте mock-рецепты в Client.

Источник данных:

```text
Client → FastAPI → TheMealDB
```

Если API не возвращает значение, интерфейс не должен придумывать его на стороне Client.

Особенно это относится к:

- calories;
- nutrition;
- preparation time;
- difficulty.

## Добавление нового фильтра

При добавлении фильтра необходимо изменить:

1. API-клиент `src/lib/api.ts`;
2. состояние фильтра в `HomeClient.tsx`;
3. dependency list загрузки;
4. backend endpoint `/api/recipes`;
5. backend-логику получения/пересечения данных;
6. при необходимости `schemas.py`.

После изменения фильтра pagination должна сбрасываться на `offset=0`.

## CORS

Backend должен разрешать origin:

```text
http://localhost:3000
```

Если frontend развёрнут на другом домене, его origin необходимо добавить в CORS-настройки FastAPI.

## Production

Перед production-развёртыванием:

- задать production `NEXT_PUBLIC_API_URL`;
- включить HTTPS;
- настроить CORS только для разрешённых origin;
- убрать debug/reload;
- проверить обработку ошибок API;
- вынести пользовательские данные из localStorage в backend при необходимости.
