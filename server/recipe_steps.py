import logging
import ssl
from hashlib import sha256
from urllib.parse import quote

import httpx
from fastapi import HTTPException

from cache import cache_get, cache_set
from config import settings
from schemas import RecipeStepsOut


logger = logging.getLogger(__name__)


def _cloud_error_payload(response: httpx.Response) -> dict:
    try:
        payload = response.json()
    except ValueError:
        return {}
    return payload if isinstance(payload, dict) else {}


async def generate_recipe_steps(title: str, instructions: str) -> RecipeStepsOut:
    function_id = settings.recipe_steps_function_id.strip()
    secret = settings.recipe_steps_function_api_key
    api_key = secret.get_secret_value().strip() if secret else ""
    missing = []
    if not function_id:
        missing.append("DISHCOVERY_RECIPE_STEPS_FUNCTION_ID")
    if not api_key:
        missing.append("DISHCOVERY_RECIPE_STEPS_FUNCTION_API_KEY")
    if missing:
        raise HTTPException(503, f"Для генерации шагов задайте {', '.join(missing)}.")

    source_hash = sha256(f"{title}\n{instructions}".encode()).hexdigest()
    cache_key = f"recipe-steps:{function_id}:{source_hash}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    try:
        async with httpx.AsyncClient(
            timeout=35.0,
            verify=ssl.create_default_context(),
            trust_env=settings.recipe_steps_use_env_proxy,
        ) as client:
            response = await client.post(
                f"https://functions.yandexcloud.net/{quote(function_id, safe='')}",
                headers={"Authorization": f"Api-Key {api_key}"},
                json={"title": title, "instructions": instructions},
            )
            response.raise_for_status()
            result = RecipeStepsOut.model_validate(response.json())
    except httpx.TimeoutException as exc:
        logger.warning("Cloud Functions request timed out (%s)", type(exc).__name__)
        raise HTTPException(504, "Генерация шагов заняла слишком много времени.") from exc
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        logger.warning(
            "Cloud Functions HTTP %s (request_id=%r, function_error=%r)",
            status,
            exc.response.headers.get("x-request-id"),
            exc.response.headers.get("x-function-error"),
        )
        if status == 504:
            raise HTTPException(504, "Генерация шагов заняла слишком много времени.") from exc
        if status == 503:
            if _cloud_error_payload(exc.response).get("error") == "Service account is not configured":
                raise HTTPException(503, "Версия облачной функции не получила IAM-токен сервисного аккаунта.") from exc
            raise HTTPException(503, "Yandex Cloud Functions сейчас недоступен.") from exc
        if status == 502:
            payload = _cloud_error_payload(exc.response)
            reason = payload.get("error")
            model_status = payload.get("model_status")
            if reason == "model_http_error" and type(model_status) is int and 400 <= model_status <= 599:
                raise HTTPException(502, f"YandexGPT ответил HTTP {model_status}.") from exc
            if reason == "model_connection_error":
                raise HTTPException(502, "Облачная функция не смогла соединиться с YandexGPT.") from exc
            if reason == "model_invalid_response":
                raise HTTPException(502, "YandexGPT вернул неполный или некорректный ответ.") from exc
            if reason == "Could not generate recipe steps":
                raise HTTPException(502, "Облачная функция запустилась, но не получила корректные шаги от YandexGPT.") from exc
        raise HTTPException(502, "Облачная функция не смогла сформировать шаги.") from exc
    except httpx.RequestError as exc:
        logger.warning("Cloud Functions connection failed (%s)", type(exc).__name__)
        raise HTTPException(502, "Не удалось связаться с облачной функцией.") from exc
    except ValueError as exc:
        logger.warning(
            "Cloud Functions returned an invalid response (request_id=%r, error=%s)",
            response.headers.get("x-request-id"),
            type(exc).__name__,
        )
        raise HTTPException(502, "Облачная функция вернула некорректный ответ.") from exc

    cache_set(cache_key, result)
    return result
