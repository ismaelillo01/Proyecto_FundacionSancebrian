from fastapi import APIRouter, HTTPException
from app.database.db import get_connection

router = APIRouter()

@router.get("/clientes")
def get_clientes_con_token():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Consulta con JOIN entre clientes y hogares para obtener token del hogar
        query = """
            SELECT c.id_cliente, c.id_hogar_url, h.token
            FROM clientes c
            JOIN hogares h ON c.id_hogar_url = h.id_hogar_url
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        clientes = []
        for row in rows:
            clientes.append({
                "id_cliente": row[0],
                "id_hogar": row[1],
                "token": row[2]
            })
        return {"success": True, "data": clientes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
