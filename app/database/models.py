# app/database/models.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database.db import Base
from sqlalchemy import Column, Integer, String, Date, Time, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from app.database.db import Base




class DatosCliente(Base):
    __tablename__ = "datos_clientes"
    id_cliente = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    apellido1 = Column(String(100), nullable=False)
    apellido2 = Column(String(100))
    dni = Column(String(9), unique=True)
    sexo = Column(String(20))
    descripcion = Column(String(500))
    fecha_nacimiento = Column(Date)
    telefono_contacto = Column(String(20))
    telefono_familiar = Column(String(20))
    fecha_registro = Column(DateTime)
    email = Column(String(255))
    id_cliente = Column(Integer, ForeignKey("clientes.id_cliente"), primary_key=True)
    cliente = relationship(
        "Cliente",
        back_populates="datos_personales",
        foreign_keys=[id_cliente] 
    )
   

class Cliente(Base):
    __tablename__ = "clientes"
    id_cliente = Column(Integer, ForeignKey("datos_clientes.id_cliente"), primary_key=True, autoincrement=True)
    id_hogar = Column(Integer, ForeignKey("hogares.id_hogar"), nullable=False)
    id_gestor = Column(Integer, ForeignKey("gestores.id_gestor"), nullable=False)
    activo = Column(Enum("activo", "inactivo", name="estado_actividad"))


    datos_personales = relationship(
        "DatosCliente",
        uselist=False,
        back_populates="cliente",
        cascade="all, delete-orphan",
        foreign_keys="[DatosCliente.id_cliente]"
    )
    horarios = relationship("Horario", back_populates="clientes")

# Tabla común
class Trabajador(Base):
    __tablename__ = "trabajadores"

    id_trabajador = Column(Integer, primary_key=True)
    nombre_usuario = Column(String(100), nullable=False, unique=True)
    contraseña = Column(String(100), nullable=False)
    nombre = Column(String(100), nullable=False)
    apellido1 = Column(String(100), nullable=False)
    apellido2 = Column(String(100))
    activo = Column(Enum("activo", "inactivo", name="estado_actividad"))


    gestor = relationship("Gestor", back_populates="trabajador", uselist=False)
    cuidador = relationship("Cuidador", back_populates="trabajador", uselist=False)

class Gestor(Base):
    __tablename__ = "gestores"

    id_gestor = Column(Integer, ForeignKey("trabajadores.id_trabajador"), primary_key=True)
    color = Column(String(7), unique=True, nullable=False)
    clientes = relationship("Cliente", backref="gestor")
    trabajador = relationship("Trabajador", back_populates="gestor")
    grupos = relationship("Formar", backref="gestor")



class Cuidador(Base):
    __tablename__ = "cuidadores"

    id_cuidador = Column(Integer, ForeignKey("trabajadores.id_trabajador"), primary_key=True)
    telefono = Column(String(20), nullable=False)

    trabajador = relationship("Trabajador", back_populates="cuidador")
    horarios = relationship("Horario", back_populates="cuidadores")
    





class Hogar(Base):
    __tablename__ = "hogares"

    id_hogar = Column(Integer, primary_key=True)
    url = Column(String(255), nullable=False)
    token = Column(String(255), nullable=False)
    codigo_postal = Column(String(5))
    provincia = Column(String(100))
    direccion = Column(String(255), nullable=False)
    activo = Column(Enum("activo", "inactivo", name="estado_actividad"))
    clientes = relationship("Cliente", backref="hogar") 

class Grupo(Base):
    __tablename__ = "grupos"

    id_grupo = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)
    gestores = relationship("Formar", backref="grupo")



class Formar(Base):
    __tablename__ = "formar"

    id_gestor = Column(Integer, ForeignKey("gestores.id_gestor"), primary_key=True)
    id_grupo = Column(Integer, ForeignKey("grupos.id_grupo"), primary_key=True)



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