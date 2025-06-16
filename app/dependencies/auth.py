#app/dependencies/auth.py
from fastapi import Request, HTTPException, status
from fastapi.responses import RedirectResponse
from app.database.db import get_connection


def require_login(request: Request):
    usuario = request.cookies.get("usuario")
    if not usuario:
        raise HTTPException(status_code=307, detail="Redirecting to login")


def get_current_user(request: Request):
    usuario = request.cookies.get("usuario")
    role = request.cookies.get("user_role")

    if not usuario or not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no autenticado"
        )

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id_trabajador FROM trabajadores WHERE nombre_usuario = %s", (usuario,))
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Trabajador no encontrado")
        id_trabajador = result[0]
    finally:
        cursor.close()
        conn.close()

    return {
        "id": id_trabajador,
        "nombre_usuario": usuario,
        "role": role
    }
