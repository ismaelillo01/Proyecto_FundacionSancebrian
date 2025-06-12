# app/database/db.py
import os
import mariadb
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Carga las variables del .env
load_dotenv()

USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASS")
HOST = os.getenv("DB_HOST")
PORT = int(os.getenv("DB_PORT"))
DATABASE = os.getenv("DB_NAME")

# Conexión con MariaDB
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

# Configuración de SQLAlchemy
DATABASE_URL = f"mysql+mariadbconnector://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()




def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()