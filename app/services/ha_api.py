import requests
from app.core.config import HA_BASE_URL, HA_TOKEN
from datetime import datetime, timedelta

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

def get_sensor_history(entity_id: str, horas: int = 24):
    """
    Consulta el historial de un sensor en las últimas `horas` horas.
    """
    start = (datetime.utcnow() - timedelta(hours=horas)).isoformat()
    url = f"{HA_BASE_URL}/api/history/period/{start}?filter_entity_id={entity_id}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return {"error": f"No se pudo obtener el historial del sensor {entity_id}"}
