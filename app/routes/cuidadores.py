#app/routes/cuidadores.py
from fastapi import APIRouter
from app.database.db import get_connection

router = APIRouter()

@router.get("/trabajadores/cuidadores")
def get_cuidadores():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id_trabajador, nombre, apellido1, apellido2 
            FROM trabajadores
            WHERE id_trabajador IN (SELECT id_cuidador FROM cuidadores)
        """)

        rows = cursor.fetchall()
        cuidadores = [{
    "id": r[0],
    "nombre": r[1],
    "apellido1": r[2],
    "apellido2": r[3]
} for r in rows]

        return {"success": True, "data": cuidadores}
    finally:
        cursor.close()
        conn.close()
