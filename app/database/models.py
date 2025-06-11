# app/database/models.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database.db import Base
from sqlalchemy import Column, Integer, String, Date, Time, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database.db import Base




class Cliente(Base):
    __tablename__ = "clientes"
    
    id_cliente = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)

    # Relación con Horario: Un cliente puede tener varios horarios
    horarios = relationship("Horario", back_populates="clientes")

# app/database/models.py
class Cuidador(Base):
    __tablename__ = "cuidadores"
    
    id_cuidador = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    apellido1 = Column(String(50), nullable=False)
    apellido2 = Column(String(50), nullable=False)

    # Relación con Horario usando una string
    horarios = relationship("Horario", back_populates="cuidadores")



class Horario(Base):
    __tablename__ = "horarios"
    
    id_horario = Column(Integer, primary_key=True, index=True)
    id_cuidador = Column(Integer, ForeignKey('cuidadores.id_cuidador'), nullable=False)
    id_cliente = Column(Integer, ForeignKey('clientes.id_cliente'), nullable=False)
    tipo_horario = Column(String(1), nullable=False)
    fecha = Column(Date, nullable=True)
    fecha_inicio = Column(Date, nullable=True)
    fecha_fin = Column(Date, nullable=True)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    color = Column(String(7), default="#3498db", nullable=False)
    descripcion = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey('horarios.id_horario'), nullable=True)
    fecha_creacion = Column(DateTime, default="CURRENT_TIMESTAMP", nullable=False)

    # Relación con Cuidador
    cuidadores = relationship("Cuidador", back_populates="horarios")
    clientes = relationship("Cliente", back_populates="horarios")
    parent = relationship("Horario", remote_side=[id_horario])

    def dict(self):
        """Convierte el objeto Horario a un diccionario para ser serializado en JSON"""
        return {
            "id_horario": self.id_horario,
            "id_cuidador": self.id_cuidador,
            "id_cliente": self.id_cliente,
            "tipo_horario": self.tipo_horario,
            "fecha": self.fecha.isoformat() if self.fecha else None,  # Convertir a string si no es None
            "fecha_inicio": self.fecha_inicio.isoformat() if self.fecha_inicio else None,  # Convertir a string si no es None
            "fecha_fin": self.fecha_fin.isoformat() if self.fecha_fin else None,  # Convertir a string si no es None
            "hora_inicio": str(self.hora_inicio),  # Asegurarse de convertir a string
            "hora_fin": str(self.hora_fin),  # Asegurarse de convertir a string
            "color": self.color,
            "descripcion": self.descripcion,
            "parent_id": self.parent_id,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None  # Convertir a string si no es None
        }