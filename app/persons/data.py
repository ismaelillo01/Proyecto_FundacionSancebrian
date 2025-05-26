from fastapi import APIRouter, HTTPException
from app.database.db import get_connection

router = APIRouter()

@router.get("/clientes")
def get_clientes():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id_cliente, nombre, apellido1, apellido2
            FROM clientes
        """)
        rows = cursor.fetchall()
        clientes = []
        for row in rows:
            clientes.append({
                "id_cliente": row[0],
                "nombre": row[1],
                "apellido1": row[2],
                "apellido2": row[3]
            })
        return {"success": True, "data": clientes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/clientes/{id_cliente}/hogar")
def get_hogar_info(id_cliente: int):
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
        return {"success": True, "data": {"url": row[0], "token": row[1]}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
