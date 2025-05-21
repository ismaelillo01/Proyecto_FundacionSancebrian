from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from app.services.ha_api import get_sensor_history
from datetime import datetime, timedelta, timezone
import pytz

router = APIRouter()

@router.get("/sensor/historico")
def sensor_historico(sensor: str = Query(...), fecha: str = Query(...), zona: str = Query("Europe/Madrid")):
    """
    Devuelve historial del sensor para la fecha indicada (YYYY-MM-DD), convertido a hora local.
    Formato: {"success": True, "data": [...], "message": None}
    """
    try:
        zona_local = pytz.timezone(zona)

        # Interpretar fecha como día completo
        fecha_inicio_local = datetime.strptime(fecha, "%Y-%m-%d").replace(tzinfo=zona_local)
        fecha_fin_local = fecha_inicio_local + timedelta(days=1)

        # Convertir a UTC para la API de Home Assistant
        fecha_inicio_utc = fecha_inicio_local.astimezone(timezone.utc)
        fecha_fin_utc = fecha_fin_local.astimezone(timezone.utc)

        # Obtener histórico desde HA
        historico = get_sensor_history(sensor, start=fecha_inicio_utc, end=fecha_fin_utc)

        if not historico or not isinstance(historico, list) or len(historico[0]) == 0:
            return {
                "success": True,
                "data": [],
                "message": f"Sin datos del sensor '{sensor}' en la fecha {fecha}"
            }

        datos = []
        for estado in historico[0]:
            try:
                fecha_utc = datetime.fromisoformat(estado["last_changed"].replace("Z", "+00:00")).astimezone(timezone.utc)
                fecha_local = fecha_utc.astimezone(zona_local)
                datos.append({
                    "x": fecha_local.strftime("%d/%m/%Y %H:%M"),
                    "y": float(estado["state"]) if estado["state"].replace(".", "", 1).isdigit() else estado["state"]
                })
            except Exception:
                continue

        return {
            "success": True,
            "sensor": sensor,
            "fecha": fecha,
            "zona": zona,
            "data": datos,
            "message": None
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": "Error al obtener el historial del sensor.",
            "detail": str(e)
        })
