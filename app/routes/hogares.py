from fastapi import APIRouter, HTTPException
from app.database.db import get_connection

router = APIRouter()

@router.get("/hogares/lista")
def get_hogares():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT direccion,id_hogar FROM hogares")
        rows = cursor.fetchall()
        direcciones = [{"id": row[1], "nombre": row[0]} for row in rows]

        return {"success": True, "data": direcciones}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()