# sensores/historico.py
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse
from app.database.db import get_connection
from app.services.ha_api import get_sensor_history
from datetime import datetime, timedelta, timezone
import pytz

router = APIRouter()

def get_url_y_token(id_cliente: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT h.id_hogar_url, h.token
            FROM hogares h
            JOIN clientes c ON c.id_hogar_url = h.id_hogar_url
            WHERE c.id_cliente = :id_cliente
        """, [id_cliente])
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Cliente no encontrado o sin hogar asignado")
        return row[0], row[1]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/sensor/historico")
def sensor_historico(
    id_cliente: int = Query(...),
    sensor: str = Query(...),
    fecha: str = Query(...),
    zona: str = Query("Europe/Madrid")
):
    """
    Devuelve historial del sensor de un cliente para la fecha indicada (YYYY-MM-DD), convertido a hora local.
    """
    try:
        zona_local = pytz.timezone(zona)

        # Obtener intervalo de fechas en UTC
        fecha_inicio_local = datetime.strptime(fecha, "%Y-%m-%d").replace(tzinfo=zona_local)
        fecha_fin_local = fecha_inicio_local + timedelta(days=1)
        fecha_inicio_utc = fecha_inicio_local.astimezone(timezone.utc)
        fecha_fin_utc = fecha_fin_local.astimezone(timezone.utc)

        # Obtener url y token desde la base de datos
        url, token = get_url_y_token(id_cliente)

        # Obtener histórico desde Home Assistant
        historico = get_sensor_history(sensor, start=fecha_inicio_utc, end=fecha_fin_utc, url=url, token=token)

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
