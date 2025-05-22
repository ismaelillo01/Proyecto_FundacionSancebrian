import requests
import os
from dotenv import load_dotenv
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from datetime import datetime
import pytz

load_dotenv()

router = APIRouter()

HOME_ASSISTANT_URL = os.getenv("HA_URL")
TOKEN = os.getenv("HA_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

TIMEZONE = pytz.timezone("Europe/Madrid")

@router.get("/sensor")
def get_sensor_state():
    url = f"{HOME_ASSISTANT_URL}/api/states"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        return JSONResponse(
            status_code=response.status_code,
            content={
                "success": False,
                "message": "No se pudo obtener el listado de sensores.",
                "detail": response.text
            }
        )

    try:
        all_entities = response.json()
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
                        formatted_time = raw_time  

                tipo = "binario" if e["entity_id"].startswith("binary_sensor.") else "numérico"

                sensors.append({
                    "entity_id": e["entity_id"],
                    "friendly_name": e["attributes"].get("friendly_name"),
                    "state": e["state"],
                    "unit": e["attributes"].get("unit_of_measurement"),
                    "device_class": e["attributes"].get("device_class"),
                    "last_updated": formatted_time,
                    "tipo": tipo
                })

        return {
            "success": True,
            "data": sensors,
            "message": None
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Error al procesar la respuesta de Home Assistant.",
                "detail": str(e)
            }
        )
