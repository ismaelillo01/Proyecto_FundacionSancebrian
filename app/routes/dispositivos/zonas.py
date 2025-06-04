# routes/dispositivos/zonas.py
from fastapi import APIRouter, HTTPException
from app.database.db import get_connection
import requests

router = APIRouter()

def get_url_y_token(id_cliente: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        print(f"Buscando hogar y token para id_cliente = {id_cliente}")
        cursor.execute("""
            SELECT h.url, h.token
            FROM hogares h
            JOIN clientes c ON c.id_hogar = h.id_hogar
            WHERE c.id_cliente = %s
        """, (id_cliente,))
        row = cursor.fetchone()
        print(f"Resultado de la consulta: {row}")
        if not row:
            raise HTTPException(status_code=404, detail="Cliente no encontrado o sin hogar asignado")
        return row[0], row[1]
    except Exception as e:
        print(f"Error en get_url_y_token: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.get("/zonas/{id_cliente}")
def get_zonas(id_cliente: int):
    url, token = get_url_y_token(id_cliente)

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(f"{url}/api/states", headers=headers, verify=False)
        response.raise_for_status()
        sensores = response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener sensores: {str(e)}")

    zonas = set()

    for sensor in sensores:
        entity_id = sensor.get("entity_id", "")
        if not entity_id.startswith(("sensor.", "binary_sensor.", "button.", "update.")):
            continue

        try:
            partes = entity_id.split(".")[1].split("_")
            if len(partes) >= 2:
                zonas.add(partes[1].lower())
        except:
            continue

    return {
        "success": True,
        "zonas": sorted(zonas)
    }
