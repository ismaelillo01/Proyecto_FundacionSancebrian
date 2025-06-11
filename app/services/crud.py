# app/services/crud.py
from sqlalchemy.orm import Session
from app.database.models import Horario
from datetime import datetime

def create_horario(db: Session, horario_data: dict):
    db_horario = Horario(
        id_cuidador=horario_data['id_cuidador'],
        id_cliente=horario_data['id_cliente'],
        tipo_horario=horario_data['tipo_horario'],
        fecha=horario_data.get('fecha'),
        fecha_inicio=horario_data.get('fecha_inicio'),
        fecha_fin=horario_data.get('fecha_fin'),
        hora_inicio=horario_data['hora_inicio'],
        hora_fin=horario_data['hora_fin'],
        color=horario_data.get('color', '#3498db'),
        descripcion=horario_data.get('descripcion'),
        parent_id=horario_data.get('parent_id'),
        fecha_creacion=datetime.now()
    )
    db.add(db_horario)
    db.commit()  # Guardar en la base de datos
    db.refresh(db_horario)  # Refresca el objeto con los datos actualizados desde la base de datos
    return db_horario
