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

def get_sensor_history(entity_id: str, start: datetime = None, end: datetime = None):
    if start is None:
        start = datetime.utcnow() - timedelta(hours=24)

    # Formateamos fechas sin microsegundos ni zona horaria
    start_str = start.strftime("%Y-%m-%dT%H:%M:%S")
    base_url = f"{HA_BASE_URL}/api/history/period/{start_str}?filter_entity_id={entity_id}"

    if end is not None:
        end_str = end.strftime("%Y-%m-%dT%H:%M:%S")
        base_url += f"&end_time={end_str}"

    response = requests.get(base_url, headers=headers)
   

    if response.status_code == 200:
        return response.json()
    return {"error": f"No se pudo obtener el historial del sensor {entity_id}"}
