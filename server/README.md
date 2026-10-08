# Dishcovery Server

Backend-приложение Dishcovery на **FastAPI**.

Server предоставляет REST API для Next.js-клиента, получает рецепты из TheMealDB, преобразует их в единый формат Dishcovery и реализует фильтрацию, Pantry Mode и пагинацию.

## Стек

- Python 3.11+;
- FastAPI;
- Pydantic;
- Uvicorn;
- HTTP-клиент для TheMealDB;
- in-memory/cache слой проекта.

## Запуск

Создать виртуальное окружение:

```bash
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows:

```powershell
.venv\Scripts\activate
```

Установить зависимости:

```bash
pip install -r requirements.txt
```

Запустить:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

API:

```text
http://localhost:8001
```

Swagger:

```text
http://localhost:8001/docs
```

## Структура

```text
server/
├── main.py
├── config.py
├── schemas.py
├── mealdb.py
├── mapper.py
├── pantry.py
├── cache.py
├── requirements.txt
└── README.md
```

## Ответственность модулей

### `main.py`

Основной FastAPI application:

- endpoints;
- query parameters;
- фильтрация;
- pagination;
- CORS;
- обработка ошибок upstream.

### `mealdb.py`

Интеграция с TheMealDB:

- поиск;
- фильтрация по кухне;
- фильтрация по категории;
- фильтрация по ингредиенту;
- получение полной карточки;
- получение metadata;
- random recipe.

### `mapper.py`

Преобразование формата TheMealDB в формат Dishcovery.

Также содержит соответствия между названиями категорий/кухонь внешнего API и названиями, используемыми в UI.

### `pantry.py`

Логика Pantry Mode:

- определение имеющихся ингредиентов;
- определение недостающих ингредиентов;
- фильтрация рецептов, которые можно приготовить из имеющихся продуктов.

### `schemas.py`

Pydantic-модели API.

### `config.py`

Конфигурация приложения, включая CORS.

### `cache.py`

Кэширование ответов upstream для уменьшения количества внешних запросов.

## API Endpoints

### Health

```http
GET /api/health
```

Проверяет состояние приложения и доступность upstream.

Пример:

```json
{
  "status": "ok",
  "upstream": "ok"
}
```

### Metadata

```http
GET /api/meta
```

Возвращает:

- кухни;
- типы блюд;
- ингредиенты;
- доступные значения дополнительных фильтров.

### Ingredients

```http
GET /api/pantry/ingredients
```

Возвращает список ингредиентов для Pantry Mode.

### Recipes

```http
GET /api/recipes
```

Параметры:

| Параметр | Тип | Описание |
|---|---|---|
| `q` | string | Поиск по названию |
| `cuisine` | string | Кухня |
| `type` | string | Тип блюда |
| `ingredient` | string | Ингредиент |
| `max_time` | integer | Максимальное время |
| `diet` | string | Диета |
| `difficulty` | string | Сложность |
| `pantry` | string | Ингредиенты через запятую |
| `only_pantry` | boolean | Только доступные рецепты |
| `limit` | integer | Размер страницы |
| `offset` | integer | Смещение |

Пример:

```http
GET /api/recipes?q=chicken&cuisine=Итальянская&type=Ужин&ingredient=Garlic&limit=24&offset=0
```

Ответ:

```json
{
  "items": [],
  "total": 120
}
```

## Комбинирование фильтров

Фильтры не являются взаимоисключающими.

Server формирует пересечение результатов:

```text
Search
  ∩ Cuisine
  ∩ Type
  ∩ Ingredient
```

Например:

```http
GET /api/recipes?q=pasta&cuisine=Итальянская&ingredient=Tomato
```

означает:

> Найти итальянские рецепты с Tomato, соответствующие поиску `pasta`.

## Типы блюд

TheMealDB использует собственные категории, например:

```text
Beef
Chicken
Pasta
Seafood
Dessert
...
```

В интерфейсе Dishcovery несколько категорий могут отображаться как один пользовательский тип.

Поэтому при выборе типа Server должен учитывать все соответствующие категории TheMealDB, а не только первую найденную категорию.

## Pantry Mode

Параметры:

```http
GET /api/recipes?pantry=Chicken,Basil
```

или:

```http
GET /api/recipes?pantry=Chicken,Basil&only_pantry=true
```

При `only_pantry=true` сервер:

1. получает полные данные рецептов;
2. сравнивает ингредиенты рецепта с Pantry;
3. определяет отсутствующие ингредиенты;
4. оставляет только подходящие рецепты.

## Pagination

TheMealDB не используется как полноценный paginated database API.

Dishcovery Server получает набор кандидатов, удаляет дубли и выполняет pagination самостоятельно:

```http
GET /api/recipes?limit=24&offset=0
GET /api/recipes?limit=24&offset=24
GET /api/recipes?limit=24&offset=48
```

`total` вычисляется до применения pagination.

Это позволяет Client понимать, есть ли следующая страница.

## Получение полной карточки

Некоторые filter endpoints TheMealDB возвращают только:

```text
idMeal
strMeal
strMealThumb
```

без полного списка ингредиентов.

Поэтому Server при необходимости выполняет дополнительный запрос по `idMeal`, чтобы получить полную информацию перед формированием `RecipeOut`.

## Mock / synthetic data

Server не должен генерировать искусственные значения для рецептов.

В частности, текущий источник не предоставляет достоверные:

- calories;
- protein/fat/carbohydrates;
- preparation time;
- difficulty.

Поэтому эти поля не должны вычисляться через hash, случайные числа или другие искусственные алгоритмы.

Схема допускает `null`:

```python
time: int | None
kcal: int | None
difficulty: str | None
```

## CORS

Для локальной разработки Client работает на:

```text
http://localhost:3000
```

Поэтому этот origin должен быть разрешён в `config.py`.

Пример:

```python
cors_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

Для production следует разрешать только реальные домены приложения.

## Обработка ошибок

Ошибка внешнего источника TheMealDB должна возвращаться клиенту как upstream error, например HTTP 502.

Клиент в таком случае показывает сообщение об ошибке вместо пустого списка рецептов.

## Добавление нового upstream-провайдера

Интеграцию желательно изолировать в отдельном модуле.

Рекомендуемая архитектура:

```text
FastAPI
   ↓
Recipe Provider interface
   ├── TheMealDB
   ├── Spoonacular
   └── другой provider
        ↓
     Mapper
        ↓
 Dishcovery schema
```

Это позволит заменить источник данных без переписывания frontend.

## PostgreSQL

Текущая версия не требует PostgreSQL для получения рецептов.

Для следующего этапа PostgreSQL рекомендуется использовать для:

- локального каталога рецептов;
- ингредиентов;
- связей recipe ↔ ingredient;
- nutrition;
- пользовательского избранного;
- истории;
- shopping lists;
- персональных рекомендаций.

Рекомендуемая базовая модель:

```text
recipes
ingredients
recipe_ingredients
nutrition
users
favorites
shopping_lists
```

## Production

Перед production-развёртыванием:

- убрать `--reload`;
- настроить HTTPS;
- ограничить CORS;
- добавить централизованное логирование;
- добавить rate limiting;
- добавить retry/timeout для upstream;
- вынести cache в Redis при необходимости;
- добавить PostgreSQL для постоянных данных;
- проверить условия использования внешнего источника.
