import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'usuarios.db')

def crear_base_datos_provisional():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                        usuario TEXT NOT NULL UNIQUE,
                                                        contrasena TEXT NOT NULL
                );
                ''')
    cur.execute("SELECT * FROM usuarios WHERE usuario = ?", ('test',))
    if not cur.fetchone():
        cur.execute("INSERT INTO usuarios (usuario, contrasena) VALUES (?, ?)", ('test', 'test123'))
        print("Usuario de prueba creado: usuario='test', contraseña='test123'")
    else:
        print("El usuario de prueba ya existe.")
    conn.commit()
    conn.close()

if __name__ == 'test':
    crear_base_datos_provisional()
