from app.database.db import get_connection

def verificar_usuario(usuario: str, password: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT COUNT(*) FROM trabajadores
            WHERE nombre_usuario = %s AND contraseña = %s
        """, (usuario, password))
        result = cursor.fetchone()
        return result and result[0] > 0
    finally:
        cursor.close()
        conn.close()
