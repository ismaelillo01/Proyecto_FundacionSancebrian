from fastapi import APIRouter
from fastapi.responses import JSONResponse
import os, requests
from dotenv import load_dotenv
from datetime import datetime
import pytz

router = APIRouter()

load_dotenv()
HOME_ASSISTANT_URL = os.getenv("HA_URL")
TOKEN = os.getenv("HA_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}
TIMEZONE = pytz.timezone("Europe/Madrid")

@router.get("/detalle")
def get_dispositivos_detalle():
    url = f"{HOME_ASSISTANT_URL}/api/states"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        return JSONResponse(
            status_code=response.status_code,
            content={"success": False, "message": "Error al obtener sensores.", "detail": response.text}
        )

    sensores_raw = response.json()
    dispositivos = {}

    for sensor in sensores_raw:
        entity_id = sensor.get("entity_id", "")
        # Filtro
        if not entity_id.startswith(("sensor.", "binary_sensor.", "button.", "update.")):
            continue

        # Obtener parte común para el id de dispositivo: tras punto hasta primer guion bajo o todo si no hay guion bajo
        id_part = entity_id.split(".", 1)[1]  
        dispositivo_id = id_part.split("_", 1)[0]  

        nombre = dispositivo_id  
        friendly = sensor["attributes"].get("friendly_name", entity_id)
        raw_time = sensor.get("last_updated", "")
        unidad = sensor["attributes"].get("unit_of_measurement")
        device_class = sensor["attributes"].get("device_class")
        valor = sensor["state"]

        try:
            dt_utc = datetime.fromisoformat(raw_time.replace("Z", "+00:00"))
            dt_local = dt_utc.astimezone(TIMEZONE)
            last_updated = dt_local.strftime("%d/%m/%Y %H:%M")
        except:
            last_updated = raw_time

        parametro = {
            "nombre": friendly,
            "valor": valor,
            "unidad": unidad,
            "device_class": device_class,
            "last_updated": last_updated,
            "entity_id": entity_id
        }

        if dispositivo_id not in dispositivos:
            dispositivos[dispositivo_id] = {
                "id": dispositivo_id,
                "nombre": nombre,
                "parametros": []
            }

        dispositivos[dispositivo_id]["parametros"].append(parametro)

    return {
        "success": True,
        "data": list(dispositivos.values()),
        "message": None
    }
