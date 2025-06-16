from fastapi import Cookie, HTTPException, APIRouter
from app.database.db import get_connection

router = APIRouter()

@router.get("/clientesActivos")
def get_clientes(usuario: str = Cookie(None)):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Consultar todos los clientes
        cursor.execute("""
            SELECT c.id_cliente, dc.nombre, dc.apellido1, dc.apellido2, c.activo, c.id_gestor
            FROM clientes c
            JOIN datos_clientes dc ON c.id_cliente = dc.id_cliente
            WHERE activo='activo'
        """)

        rows = cursor.fetchall()
        clientes = [{
            "id_cliente": row[0],
            "nombre": row[1],
            "apellido1": row[2],
            "apellido2": row[3],
            "activo": row[4],
            "id_gestor": row[5]
        } for row in rows]

        return {"success": True, "data": clientes}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()




@router.get("/clientesInactivos")
def get_clientes(usuario: str = Cookie(None)):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Consultar todos los clientes
        cursor.execute("""
            SELECT c.id_cliente, dc.nombre, dc.apellido1, dc.apellido2, c.activo, c.id_gestor
            FROM clientes c
            JOIN datos_clientes dc ON c.id_cliente = dc.id_cliente
            WHERE activo='inactivo'
        """)

        rows = cursor.fetchall()
        clientes = [{
            "id_cliente": row[0],
            "nombre": row[1],
            "apellido1": row[2],
            "apellido2": row[3],
            "activo": row[4],
            "id_gestor": row[5]
        } for row in rows]

        return {"success": True, "data": clientes}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

