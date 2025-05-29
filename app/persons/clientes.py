from fastapi import APIRouter, HTTPException
from app.database.db import get_connection

router = APIRouter()

@router.get("/clientes/{id_cliente}")
def get_cliente_detalle(id_cliente: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                c.nombre, c.apellido1, c.apellido2, c.dni, c.fecha_registro,
                h.direccion, h.cp, c.descripcion, h.provincia, c.fecha_nacimiento, c.sexo
            FROM clientes c
            LEFT JOIN hogares h ON c.id_hogar_url = h.id_hogar_url
            WHERE c.id_cliente = :1
        """, [id_cliente])

        row = cursor.fetchone()

        if row:
            return {
                "success": True,
                "data": {
                    "nombre": row[0],
                    "apellido1": row[1],
                    "apellido2": row[2],
                    "dni": row[3],
                    "fecha_registro": row[4],
                    "direccion": row[5],
                    "cp": row[6],
                    "descripcion": row[7],
                    "provincia": row[8],
                    "fecha_nacimiento": row[9],
                    "sexo": row[10]
                }
            }
        else:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
