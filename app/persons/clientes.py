#app/persons/clientes.py
from fastapi import APIRouter, HTTPException
from app.database.db import get_connection
from fastapi import Cookie
router = APIRouter()

@router.get("/clientes/{id_cliente}")
def get_cliente_detalle(
    id_cliente: int,
    user_role: str = Cookie(None),
    usuario: str = Cookie(None)
):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if user_role == "gestor":
            # gestores pueden acceder a cualquier cliente
            pass  # no filtro especial aquí
        elif user_role == "cuidador":
            # cuidadores solo si tienen horario con ese cliente
            cursor.execute("SELECT id_cuidador FROM cuidadores WHERE usuario = %s", (usuario,))
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=403, detail="Cuidador no autorizado")
            id_cuidador = result[0]

            cursor.execute("""
                SELECT 1 FROM horarios
                WHERE id_cuidador = %s AND id_cliente = %s
            """, (id_cuidador, id_cliente))
            acceso = cursor.fetchone()
            if not acceso:
                raise HTTPException(status_code=403, detail="Acceso denegado a cliente")

        # Consulta detalles cliente
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

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

