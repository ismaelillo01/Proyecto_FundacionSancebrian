from fastapi import Cookie, HTTPException, APIRouter
from app.database.db import get_connection

router = APIRouter()

@router.get("/cuidadoresActivos")
def get_cuidadores(usuario: str = Cookie(None)):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Consultar todos los clientes
        cursor.execute("""
            SELECT c.id_cuidador, t.nombre, t.apellido1, t.apellido2, t.nombre_usuario, t.contraseña, t.activo, c.telefono
            FROM trabajadores t
            JOIN cuidadores c on t.id_trabajador = c.id_cuidador
            WHERE activo='activo'
        """)

        rows = cursor.fetchall()
        cuidadores = [{
            "id_cuidador": row[0],
            "nombre": row[1],
            "apellido1": row[2],
            "apellido2": row[3],
            "nombre_usuario": row[4],
            "contraseña": row[5],
            "activo": row[6],
            "telefono": row[7]
        } for row in rows]

        return {"success": True, "data": cuidadores}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()




@router.get("/cuidadoresInactivos")
def get_cuidadores(usuario: str = Cookie(None)):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Consultar todos los clientes
        cursor.execute("""
            SELECT c.id_cuidador, t.nombre, t.apellido1, t.apellido2, t.nombre_usuario, t.contraseña, t.activo, c.telefono
            FROM trabajadores t
            JOIN cuidadores c on t.id_trabajador = c.id_cuidador
            WHERE activo='inactivo'
        """)

        rows = cursor.fetchall()
        cuidadores = [{
            "id_cuidador": row[0],
            "nombre": row[1],
            "apellido1": row[2],
            "apellido2": row[3],
            "nombre_usuario": row[4],
            "contraseña": row[5],
            "activo": row[6],
            "telefono": row[7]
        } for row in rows]

        return {"success": True, "data": cuidadores}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()