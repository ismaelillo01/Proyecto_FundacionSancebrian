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
                dc.nombre, dc.apellido1, dc.apellido2, dc.dni, dc.fecha_registro,
                h.direccion, h.codigo_postal, h.provincia,
                dc.descripcion, dc.fecha_nacimiento,
                h.token, h.url,
                dc.telefono_contacto, dc.telefono_familiar, dc.sexo
            FROM datos_clientes dc
            JOIN clientes c ON dc.id_cliente = c.id_cliente
            JOIN hogares h ON c.id_hogar = h.id_hogar
            WHERE c.id_cliente = %s
        """, (id_cliente,))

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
                    "codigo_postal": row[6],
                    "provincia": row[7],
                    "descripcion": row[8],
                    "fecha_nacimiento": row[9],
                    "token": row[10],
                    "url": row[11],
                    "telefono_contacto": row[12],
                    "telefono_familiar": row[13],
                    "sexo": row[14]
                }
            }
        else:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
