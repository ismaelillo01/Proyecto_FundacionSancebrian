#app/routes/administracion/trabajadores/verGestores.py
from fastapi import Cookie, HTTPException, APIRouter
from app.database.db import get_connection

router = APIRouter()

@router.get("/gestoresActivos")
def get_gestores(usuario: str = Cookie(None)):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Consultar todos los clientes
        cursor.execute("""
            SELECT g.id_gestor, t.nombre, t.apellido1, t.apellido2, t.nombre_usuario, t.contraseña, t.activo, g.color
            FROM trabajadores t
            JOIN gestores g on t.id_trabajador = g.id_gestor
            WHERE activo='activo'
        """)

        rows = cursor.fetchall()
        gestores = [{
            "id_gestor": row[0],
            "nombre": row[1],
            "apellido1": row[2],
            "apellido2": row[3],
            "nombre_usuario": row[4],
            "contraseña": row[5],
            "activo": row[6],
            "color": row[7]
        } for row in rows]

        return {"success": True, "data": gestores}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()





@router.get("/gestoresInactivos")
def get_gestores(usuario: str = Cookie(None)):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Consultar todos los clientes
        cursor.execute("""
            SELECT g.id_gestor, t.nombre, t.apellido1, t.apellido2, t.nombre_usuario, t.contraseña, t.activo, g.color
            FROM trabajadores t
            JOIN gestores g on t.id_trabajador = g.id_gestor
            WHERE activo='inactivo'
        """)

        rows = cursor.fetchall()
        gestores = [{
            "id_gestor": row[0],
            "nombre": row[1],
            "apellido1": row[2],
            "apellido2": row[3],
            "nombre_usuario": row[4],
            "contraseña": row[5],
            "activo": row[6],
            "color": row[7]
        } for row in rows]

        return {"success": True, "data": gestores}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()