import requests
import os
from dotenv import load_dotenv
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from datetime import datetime
import pytz  # Asegúrate de tenerlo instalado: pip install pytz

load_dotenv()

router = APIRouter()

HOME_ASSISTANT_URL = os.getenv("HA_URL")
TOKEN = os.getenv("HA_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Define la zona horaria española
TIMEZONE = pytz.timezone("Europe/Madrid")

@router.get("/sensor")
def get_sensor_state():
    url = f"{HOME_ASSISTANT_URL}/api/states"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        all_entities = response.json()

        # Extraer sensores estándar y binarios, incluyendo vibración
        sensors = []
        for e in all_entities:
            if (
                e["entity_id"].startswith(("sensor.", "binary_sensor."))
                or "vibration" in e["entity_id"]
                or (e.get("device_class") and "vibration" in e["device_class"])
            ):
                raw_time = e.get("last_updated")
                formatted_time = None

                if raw_time:
                    try:
                        dt_utc = datetime.fromisoformat(raw_time.replace("Z", "+00:00"))
                        dt_local = dt_utc.astimezone(TIMEZONE)
                        formatted_time = dt_local.strftime("%d/%m/%Y %H:%M")
                    except Exception:
                        formatted_time = raw_time  # fallback si falla el formateo

                sensors.append({
                    "entity_id": e["entity_id"],
                    "friendly_name": e["attributes"].get("friendly_name"),
                    "state": e["state"],
                    "unit": e["attributes"].get("unit_of_measurement"),
                    "device_class": e["attributes"].get("device_class"),
                    "last_updated": formatted_time
                })

        return {"sensors": sensors}

    else:
        return JSONResponse(
            status_code=response.status_code,
            content={"error": "No se pudo obtener el sensor", "detail": response.text}
        )
