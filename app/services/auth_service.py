from app.database.db import get_connection

def verificar_usuario(usuario: str, password: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT COUNT(*) FROM usuarios
            WHERE nombre_usuario = :usuario AND contraseña = :password
        """, {"usuario": usuario, "password": password})
        result = cursor.fetchone()
        return result and result[0] > 0
    finally:
        cursor.close()
        conn.close()
