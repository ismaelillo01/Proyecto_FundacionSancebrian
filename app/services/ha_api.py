import requests
from app.core.config import HA_BASE_URL, HA_TOKEN

headers = {
    "Authorization": f"Bearer {HA_TOKEN}",
    "Content-Type": "application/json",
}

def get_sensor_state(entity_id: str):
    url = f"{HA_BASE_URL}/api/states/{entity_id}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return {"error": "No se pudo obtener el estado del sensor"}
