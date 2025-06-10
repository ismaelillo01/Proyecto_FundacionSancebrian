from fastapi import Cookie, HTTPException
from app.database.db import get_connection
from fastapi import APIRouter
router = APIRouter()


@router.get("/clientes")
def get_clientes(user_role: str = Cookie(None), usuario: str = Cookie(None)):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        if user_role == "gestor":
            # gestores ven todos
            cursor.execute("""
                SELECT c.id_cliente, dc.nombre, dc.apellido1, dc.apellido2
                FROM clientes c
                JOIN datos_clientes dc ON c.id_cliente = dc.id_cliente
            """)
        elif user_role == "cuidador":
            # cuidadores ven solo sus clientes según tabla horarios
            # primero obtener id_cuidador del usuario actual (supongo que usuario es el nombre o id cuidador)
            cursor.execute("""
                SELECT t.id_trabajador
                FROM trabajadores t
                JOIN cuidadores c ON t.id_trabajador = c.id_cuidador
                WHERE t.nombre_usuario = %s
            """, (usuario,))
            result = cursor.fetchone()
            print("DEBUG id_cuidador obtenido:", result)

            if not result:
                return {"success": False, "data": [], "msg": "Cuidador no encontrado"}
            id_cuidador = result[0]

            cursor.execute("""
                SELECT DISTINCT c.id_cliente, dc.nombre, dc.apellido1, dc.apellido2
                FROM clientes c
                JOIN datos_clientes dc ON c.id_cliente = dc.id_cliente
                JOIN horarios h ON c.id_cliente = h.id_cliente
                WHERE h.id_cuidador = %s
            """, (id_cuidador,))
        else:
            # no rol válido, vaciar lista
            return {"success": False, "data": [], "msg": "Rol no autorizado"}

        rows = cursor.fetchall()
        clientes = [{
            "id_cliente": row[0],
            "nombre": row[1],
            "apellido1": row[2],
            "apellido2": row[3]
        } for row in rows]

        return {"success": True, "data": clientes}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
