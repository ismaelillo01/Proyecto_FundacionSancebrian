#app/services/ha_api.py
import requests
from datetime import datetime, timedelta

def get_sensor_history(entity_id: str, start: datetime = None, end: datetime = None, url: str = None, token: str = None):
    if start is None:
        start = datetime.utcnow() - timedelta(hours=24)

    if not url or not token:
        raise ValueError("Se requiere URL y token de Home Assistant.")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    start_str = start.strftime("%Y-%m-%dT%H:%M:%S")
    base_url = f"{url}/api/history/period/{start_str}"
    params = f"?filter_entity_id={entity_id}"

    if end is not None:
        end_str = end.strftime("%Y-%m-%dT%H:%M:%S")
        params += f"&end_time={end_str}"

    params += "&minimal_response=false"

    full_url = base_url + params

    response = requests.get(full_url, headers=headers, verify=False)

    if response.status_code == 200:
        return response.json()

    raise Exception(f"Error al obtener historial del sensor '{entity_id}': {response.status_code} - {response.text}")
