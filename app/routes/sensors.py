import requests
import os
from dotenv import load_dotenv
from fastapi import APIRouter
from fastapi.responses import JSONResponse

load_dotenv()

router = APIRouter()

HOME_ASSISTANT_URL = os.getenv("HA_URL")  # corregido el typo: HA_URl → HA_URL
TOKEN = os.getenv("HA_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

@router.get("/sensor")
def get_sensor_state():
    url = f"{HOME_ASSISTANT_URL}/api/states"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        all_entities = response.json()

        # Extraer solo sensores y sus datos clave
        sensors = [
            {
                "entity_id": e["entity_id"],
                "friendly_name": e["attributes"].get("friendly_name"),
                "state": e["state"],
                "unit": e["attributes"].get("unit_of_measurement"),
                "device_class": e["attributes"].get("device_class"),
                "last_updated": e["last_updated"]
            }
            for e in all_entities if e["entity_id"].startswith("sensor.")
        ]

        return {"sensors": sensors}

    else:
        return JSONResponse(
            status_code=response.status_code,
            content={"error": "No se pudo obtener el sensor", "detail": response.text}
        )
