# sensores/historico.py
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse
from app.database.db import get_connection
from app.services.ha_api import get_sensor_history
from datetime import datetime, timedelta, timezone
import pytz
from fastapi import Request
from pydantic import BaseModel
from typing import List, Dict, Any

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
    Devuelve historial del sensor de un cliente en formato compatible con Grafana.
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

        datapoints = []
        if historico and isinstance(historico, list) and len(historico) > 0:
            for estado in historico[0]:
                try:
                    fecha_utc = datetime.fromisoformat(estado["last_changed"].replace("Z", "+00:00")).astimezone(timezone.utc)
                    timestamp_ms = int(fecha_utc.timestamp() * 1000)

                    valor = estado["state"].replace(",", ".")
                    try:
                        valor = float(valor)
                    except ValueError:
                        valor = None


                    datapoints.append([valor, timestamp_ms])
                except Exception:
                    continue

        datapoints.sort(key=lambda x: x[1])
        return [
            {
                "target": sensor,
                "datapoints": datapoints
            }
        ]

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "message": "Error al obtener el historial del sensor.",
            "detail": str(e)
        })
