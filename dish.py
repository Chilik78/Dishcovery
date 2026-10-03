from fastapi import FastAPI, APIRouter
import requests

app = FastAPI(
    title="meal_api", openapi_url="/openapi.json"
)

api_router = APIRouter()

@api_router.get("/search", status_code=200)
def search_meals(s: str = None, f: str = None):
    """
    Search meals by name (s) or first letter (f).
    Example: /search?s=Arrabiata
             /search?f=a
    """
    if s:
        url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={s}"
    elif f:
        url = f"https://www.themealdb.com/api/json/v1/1/search.php?f={f}"
    else:
        return {"error": "Please provide either 's' or 'f' parameter"}

    try:
        req = requests.get(url)
        if req.status_code == 200:
            res_json = req.json()
            if not type(res_json["meals"]) is list:
                return res_json["meals"]
            meals = [{i["idMeal"]: i["strMeal"]} for i in res_json["meals"]]
            res = {"meals": meals}
            return res
        else:
            return {"error": f"Request failed with status {req.status_code}"}
    except Exception as e:
        return {"error": str(e)}

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")