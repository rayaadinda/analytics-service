import os
import httpx

BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://backend-v2-api:5000/api")
if "localhost" in BACKEND_API_URL and not os.getenv("BACKEND_API_URL"):
    # Fallback for local testing outside docker
    BACKEND_API_URL = "http://localhost:5000/api"

async def save_clustering_results(payload: dict, token: str):
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    
    # Internal docker network host is usually the container name
    # e.g., http://backend-v2-api:5000/api/analytics/results
    url = f"{BACKEND_API_URL}/analytics/results"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
