import oracledb
import os
from dotenv import load_dotenv

# Carga las variables del .env
load_dotenv()

USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASS")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
SERVICE_NAME = os.getenv("DB_SERVICE")

# Construcción del DSN (identificador de servicio)
dsn = f"{HOST}:{PORT}/{SERVICE_NAME}"

def get_connection():
    return oracledb.connect(
        user=USER,
        password=PASSWORD,
        dsn=dsn
    )
