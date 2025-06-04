import mariadb
import os
from dotenv import load_dotenv

# Carga las variables del .env
load_dotenv()

USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASS")
HOST = os.getenv("DB_HOST")
PORT = int(os.getenv("DB_PORT"))  
DATABASE = os.getenv("DB_NAME")   

def get_connection():
    try:
        conn = mariadb.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            database=DATABASE
        )
        return conn
    except mariadb.Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None
