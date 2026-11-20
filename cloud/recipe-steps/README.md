# Пошаговые инструкции в Yandex Cloud

Кнопка «Показать по шагам» в карточке вызывает FastAPI. Сервер отправляет название и исходную инструкцию в приватную Yandex Cloud Function. Функция обращается к YandexGPT и возвращает JSON со списком шагов на русском.

## Развёртывание

1. Создайте сервисный аккаунт для функции и выдайте ему роль `ai.languageModels.user` на каталог, где будет создана функция. Обработчик получает IAM-токен этого аккаунта из контекста выполнения. [Авторизация в контексте функции](https://yandex.cloud/ru/docs/functions/lang/python/context)
2. Создайте приватную функцию в Yandex Cloud Functions. Добавьте содержимое [index.py](index.py) через встроенный редактор или загрузите ZIP с этим файлом в корне. Укажите среду **Python 3.12**, точку входа `index.handler`, память **128 МБ** и таймаут **30 секунд**. Прикрепите сервисный аккаунт из шага 1 и опубликуйте версию. [Создание функции на Python](https://yandex.cloud/ru/docs/functions/quickstart/create-function/python-function-quickstart)
3. Создайте сервисный аккаунт для FastAPI. Выдайте ему роль `functions.functionInvoker` на функцию и выпустите для этого же аккаунта API-ключ с областью действия `yc.serverless.functions.invoke`. Сохраните секретное значение из поля `secret` при создании ключа. [Назначение роли на функцию](https://yandex.cloud/ru/docs/functions/operations/function/role-add) · [Создание API-ключа](https://yandex.cloud/ru/docs/iam/operations/authentication/manage-api-keys)
4. Для локального запуска создайте файл `server/.env` и подставьте ID функции и секретное значение ключа её вызова.

   ```dotenv
   DISHCOVERY_RECIPE_STEPS_FUNCTION_ID=<идентификатор функции>
   DISHCOVERY_RECIPE_STEPS_FUNCTION_API_KEY=<секретное значение API-ключа вызова функции>
   ```

   или

   ```powershell
   $env:DISHCOVERY_RECIPE_STEPS_FUNCTION_ID='<идентификатор функции>'
   $env:DISHCOVERY_RECIPE_STEPS_FUNCTION_API_KEY='<секретное значение API-ключа вызова функции>'
   ```

   Затем запустите сервер из корня проекта.

   ```powershell
   cd server
   uvicorn main:app --host 0.0.0.0 --port 8001
   ```

Файл `server/.env` исключён из Git. Переменные окружения процесса переопределяют значения из файла. Функция использует модель `yandexgpt-5.1` со структурированным JSON-ответом. [API генерации текста](https://aistudio.yandex.ru/ru/docs/ai-studio/text-generation/api-ref/TextGeneration/completion)

## Проверка

Запустите Next.js, откройте рецепт с исходной инструкцией и нажмите «Показать по шагам». В карточке появится нумерованный список. Тот же сценарий можно проверить вызовом `POST /api/recipes/{recipe_id}/steps` через Swagger на `http://localhost:8001/docs`.

## Ошибки 502 и 503

В терминале FastAPI строка `Cloud Functions HTTP …` показывает исходный статус и идентификатор запроса. Если сервис ответил `401` или `403`, проверьте ключ вызова, его область действия и роль `functions.functionInvoker`. При `404` сверьте ID функции с последним сегментом ссылки для вызова и убедитесь, что опубликована версия. При `5xx` используйте идентификатор запроса для поиска вызова в журнале функции или в обращении в поддержку, если журнал недоступен. [Просмотр логов функции](https://yandex.cloud/ru/docs/functions/operations/function/function-logs)

При `503` проверьте поле `detail` в ответе FastAPI через Swagger. Если версия функции не получила IAM-токен, проверьте, что в опубликованной версии выбран сервисный аккаунт из шага 1 с ролью `ai.languageModels.user`. Если FastAPI сообщает о недоступности Cloud Functions, проверьте состояние сервиса в консоли Yandex Cloud. [IAM-токен сервисного аккаунта](https://yandex.cloud/ru/docs/functions/operations/function-sa)

При `502` проверьте поле `detail` после публикации актуальной версии [index.py](index.py) и перезапуска FastAPI. Если в ответе есть `YandexGPT ответил HTTP 403`, проверьте доступ сервисного аккаунта функции к модели в её каталоге. Если указано, что ответ модели неполный или некорректный, идентификатор вызова Cloud Functions поможет найти соответствующую запись. [Коды ошибок Yandex AI Studio](https://aistudio.yandex.ru/ru/docs/ai-studio/troubleshooting/error-codes)

FastAPI по умолчанию подключается к Cloud Functions напрямую и проверяет TLS через системное хранилище сертификатов. Если терминал показывает `Cloud Functions connection failed (ConnectError)`, проверьте доступность прямого соединения.

```powershell
curl.exe --noproxy functions.yandexcloud.net -I https://functions.yandexcloud.net/
```

Если в вашей сети необходим прокси, задайте переменную ниже перед запуском FastAPI. Cloud Functions будет использовать настройки прокси из окружения.

```powershell
$env:DISHCOVERY_RECIPE_STEPS_USE_ENV_PROXY = 'true'
```

