from fastapi import APIRouter, HTTPException
from app.database.db import get_connection

router = APIRouter()

@router.get("/VerHogaresActivos")
def get_hogares():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT direccion,id_hogar, url, token, activo, codigo_postal, provincia " \
        "FROM hogares WHERE activo='activo'")
        rows = cursor.fetchall()
        direcciones = [{"id": row[1], 
                        "direccion": row[0],
                        "url": row[2],
                        "token": row[3],
                        "activo": row[4],
                        "Cod_Postal": row[5],
                        "Provincia": row[6]
                        } for row in rows]

        return {"success": True, "data": direcciones}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()



@router.get("/VerHogaresInactivos")
def get_hogares():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT direccion,id_hogar, url, token, activo, codigo_postal, provincia " \
        "FROM hogares WHERE activo='inactivo'")
        rows = cursor.fetchall()
        direcciones = [{"id": row[1], 
                        "direccion": row[0],
                        "url": row[2],
                        "token": row[3],
                        "activo": row[4],
                        "Cod_Postal": row[5],
                        "Provincia": row[6]
                        } for row in rows]

        return {"success": True, "data": direcciones}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()