#app/models/user.py
from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class UserLogin(BaseModel):
    usuario: str
    password: str

class DatosClienteBase(BaseModel):
    nombre: str
    apellido1: str
    apellido2: Optional[str] = None
    dni: Optional[str] = None
    sexo: Optional[str] = None
    descripcion: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    telefono_contacto: Optional[str] = None
    telefono_familiar: Optional[str] = None
    email: Optional[str] = None

class ClienteCreate(DatosClienteBase):
    id_hogar: int
    id_gestor: int
    activo: Optional[str] = None

class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido1: Optional[str] = None
    apellido2: Optional[str] = None
    dni: Optional[str] = None
    sexo: Optional[str] = None
    descripcion: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    telefono_contacto: Optional[str] = None
    telefono_familiar: Optional[str] = None
    email: Optional[str] = None
    activo: Optional[str] = None

class TrabajadorBase(BaseModel):
    nombre_usuario: str
    nombre: str
    apellido1: str
    apellido2: Optional[str] = None

class TrabajadorCreate(TrabajadorBase):
    contraseña: str

class CuidadorData(BaseModel):
    telefono: str

class GestorData(BaseModel):
    color: str

class TrabajadorUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido1: Optional[str] = None
    apellido2: Optional[str] = None
    nombre_usuario: Optional[str] = None
    contraseña: Optional[str] = None
    activo: Optional[str] = None
    cuidador_data: Optional[CuidadorData] = None
    gestor_data: Optional[GestorData] = None

class HogarBase(BaseModel):
    url: str
    token: str
    direccion: str
    codigo_postal: Optional[str] = None
    provincia: Optional[str] = None

class HogarCreate(HogarBase):
    pass

class HogarUpdate(BaseModel):
    url: Optional[str] = None
    token: Optional[str] = None
    direccion: Optional[str] = None
    codigo_postal: Optional[str] = None
    provincia: Optional[str] = None
    activo: Optional[str] = None

class GrupoBase(BaseModel):
    nombre: str

class FormarBase(BaseModel):
    id_gestor: int
    id_grupo: int

# Response models
class ClienteResponse(DatosClienteBase):
    id_cliente: int
    fecha_registro: datetime
    activo: str

    class Config:
        from_attributes = True

class TrabajadorResponse(TrabajadorBase):
    id_trabajador: int
    activo: str

    class Config:
        from_attributes = True

class GestorResponse(TrabajadorResponse):
    color: str

    class Config:
        from_attributes = True

class CuidadorResponse(TrabajadorResponse):
    telefono: str

    class Config:
        from_attributes = True

class HogarResponse(HogarBase):
    id_hogar: int
    activo: str

    class Config:
        from_attributes = True

class GrupoResponse(GrupoBase):
    id_grupo: int

    class Config:
        from_attributes = True