from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from app.services.ha_api import get_sensor_history
from datetime import datetime, timezone
import pytz

router = APIRouter()

@router.get("/sensor/historico")
def sensor_historico(sensor: str = Query(...), dias: int = Query(2), zona: str = Query("Europe/Madrid")):
    """
    Devuelve historial desde hace `dias` días hasta ahora, convertido a hora local.
    Formato listo para graficar: [{x: "dd/mm/yyyy HH:MM", y: valor}]
    """
    try:
        historico = get_sensor_history(sensor, dias)

        if not historico or not isinstance(historico, list):
            return JSONResponse(status_code=404, content={"error": "Sin datos del historial."})

        zona_local = pytz.timezone(zona)
        datos = []

        for estado in historico[0]:  # primer sensor
            try:
                fecha_utc = datetime.fromisoformat(estado["last_changed"].replace("Z", "+00:00")).astimezone(timezone.utc)
                fecha_local = fecha_utc.astimezone(zona_local)
                datos.append({
                    "x": fecha_local.strftime("%d/%m/%Y %H:%M"),
                    "y": float(estado["state"]) if estado["state"].replace(".", "", 1).isdigit() else estado["state"]
                })
            except Exception:
                continue  # ignora errores de formato

        return datos

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
