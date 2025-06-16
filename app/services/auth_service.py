#app/services/auth_service.py
from app.database.db import get_connection

def verificar_usuario(usuario: str, password: str) -> tuple[bool, str | None]:
    print(f"[DEBUG] Entrando en verificar_usuario con usuario={usuario}, password={password}")
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Verificamos credenciales y obtenemos id_trabajador
        cursor.execute("""
            SELECT id_trabajador FROM trabajadores
            WHERE nombre_usuario = %s AND contraseña = %s
        """, (usuario, password))
        result = cursor.fetchone()
        if not result:
            return False, None

        id_trabajador = result[0]

        # Comprobamos si es gestor
        cursor.execute("SELECT 1 FROM gestores WHERE id_gestor = %s", (id_trabajador,))
        if cursor.fetchone():
            return True, "gestor"

        # Comprobamos si es cuidador
        cursor.execute("SELECT 1 FROM cuidadores WHERE id_cuidador = %s", (id_trabajador,))
        if cursor.fetchone():
            return True, "cuidador"

        # Usuario sin rol válido
        return False, None

    finally:
        cursor.close()
        conn.close()
