import oracledb
import os
from dotenv import load_dotenv

load_dotenv()

USER = os.getenv("DB_USER")  
PASSWORD = os.getenv("DB_PASS")  
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
SERVICE_NAME = os.getenv("DB_SERVICE")


dsn = f"{HOST}:{PORT}/{SERVICE_NAME}"


connection = oracledb.connect(
    user=USER,
    password=PASSWORD,
    dsn=dsn,
    mode=oracledb.DEFAULT_AUTH,
)

def get_connection():
    return connection
