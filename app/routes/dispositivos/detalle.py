from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import requests
from datetime import datetime
import pytz
from app.database.db import get_connection

router = APIRouter()

TIMEZONE = pytz.timezone("Europe/Madrid")

def get_url_y_token(id_cliente: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT h.url, h.token
            FROM hogares h
            JOIN clientes c ON c.id_hogar = h.id_hogar
            WHERE c.id_cliente = %s
        """, (id_cliente,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Cliente no encontrado o sin hogar asignado")
        return row[0], row[1]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/detalle/{id_cliente}")
def get_dispositivos_detalle(id_cliente: int):
    HOME_ASSISTANT_URL, TOKEN = get_url_y_token(id_cliente)

    HEADERS = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    url = f"{HOME_ASSISTANT_URL}/api/states"
    response = requests.get(url, headers=HEADERS, verify=False)

    if response.status_code != 200:
        return JSONResponse(
            status_code=response.status_code,
            content={
                "success": False,
                "message": f"Error al obtener sensores desde Home Assistant. Código: {response.status_code}",
                "response_text": response.text
            }
        )

    try:
        sensores_raw = response.json()
    except ValueError:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "La respuesta no es JSON válido. Revisa la URL, el token o los permisos.",
                "response_text": response.text
            }
        )

    dispositivos = {}

    for sensor in sensores_raw:
        entity_id = sensor.get("entity_id", "")
        if not entity_id.startswith(("sensor.", "binary_sensor.", "button.", "update.")):
            continue

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
