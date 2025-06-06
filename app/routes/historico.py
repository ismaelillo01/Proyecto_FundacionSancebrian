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

@router.get("/sensor/historico")
def sensor_historico(
    id_cliente: int = Query(...),
    sensor: str = Query(...),
    fecha: str = Query(...),
    zona: str = Query("Europe/Madrid")
):
    """
    Devuelve el historial del sensor de un cliente como lista de objetos con timestamp y valor.
    """
    try:
        zona_local = pytz.timezone(zona)

        # Intervalo en UTC
        fecha_base = datetime.strptime(fecha, "%Y-%m-%d")
        fecha_inicio_local = zona_local.localize(datetime.combine(fecha_base.date(), datetime.min.time()))
        fecha_fin_local = fecha_inicio_local + timedelta(days=1)
        fecha_inicio_utc = fecha_inicio_local.astimezone(timezone.utc)
        fecha_fin_utc = fecha_fin_local.astimezone(timezone.utc)

        # URL y token
        url, token = get_url_y_token(id_cliente)

        # Llamada al API de Home Assistant
        historico = get_sensor_history(sensor, start=fecha_inicio_utc, end=fecha_fin_utc, url=url, token=token)

        datos = []
        if historico and isinstance(historico, list) and len(historico) > 0:
            for estado in historico[0]:
                try:
                    # Convertir fecha del sensor (en UTC) a zona local
                    fecha_utc = datetime.fromisoformat(estado["last_changed"].replace("Z", "+00:00"))
                    fecha_local = fecha_utc.astimezone(zona_local)
                    timestamp_ms = int(fecha_local.timestamp() * 1000)

                    estado_bruto = estado["state"]
                    valor_numerico = None

                    # Intentamos convertir a número si es posible
                    try:
                        valor_numerico = float(estado_bruto.replace(",", "."))
                    except (ValueError, AttributeError):
                        valor_numerico = 1.0 if estado_bruto.lower() in ["on", "true", "detected"] else 0.0 if estado_bruto.lower() in ["off", "false", "clear"] else None

                    if valor_numerico is not None:
                        datos.append({
                            "timestamp": timestamp_ms,
                            "valor": valor_numerico
                        })

                except Exception:
                    continue

        datos.sort(key=lambda x: x["timestamp"])
        return {
            "sensor": sensor,
            "datos": datos
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "message": "Error al obtener el historial del sensor.",
            "detail": str(e)
        })
