#app/routes/verhorario.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db, get_connection
from app.dependencies.auth import get_current_user
from app.database.models import Horario

def segundos_a_hora(segundos: int) -> str:
    h = segundos // 3600
    m = (segundos % 3600) // 60
    return f"{h:02}:{m:02}"

router = APIRouter(prefix="/horarios", tags=["Horarios"])

@router.get("/mi-horario")
def get_horarios_cuidador_actual(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "cuidador":
        raise HTTPException(status_code=403, detail="Solo cuidadores pueden acceder a su horario.")

    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Obtener horarios del cuidador
        cursor.execute("""
            SELECT *
            FROM horarios
            WHERE id_cuidador = %s
        """, (current_user["id"],))
        rows = cursor.fetchall()
        columnas = [col[0] for col in cursor.description]

        horarios = []
        for row in rows:
            h = dict(zip(columnas, row))

            # 🔧 Conversión forzada de segundos a "HH:MM"
            try:
                h["hora_inicio"] = segundos_a_hora(int(h["hora_inicio"]))
                h["hora_fin"] = segundos_a_hora(int(h["hora_fin"]))
            except Exception as conv_error:
                print("[ERROR] Fallo al convertir horas:", conv_error)
                h["hora_inicio"] = "00:00"
                h["hora_fin"] = "00:00"

            # Obtener nombre del cliente desde datos_clientes
            cursor.execute("""
                SELECT nombre, apellido1, apellido2
                FROM datos_clientes
                WHERE id_cliente = %s
            """, (h["id_cliente"],))
            cliente = cursor.fetchone()

            if cliente:
                nombre_cliente = " ".join(filter(None, cliente)).strip()
            else:
                nombre_cliente = f"Usuario {h['id_cliente']}"

            h["nombre_cliente"] = nombre_cliente
            horarios.append(h)

        return horarios

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.get("/todos")
def get_todos_los_horarios(db: Session = Depends(get_db)):
    horarios = db.query(Horario).all()
    return [h.dict() for h in horarios]
