from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from app.database.db import get_db
from app.database.models import Trabajador, Cuidador, Gestor
from app.models.user import TrabajadorUpdate, CuidadorData, GestorData

router = APIRouter(
    prefix="/trabajadores",
    tags=["Trabajadores"]
)

@router.put("/{id_trabajador}",
           response_model=dict,
           status_code=status.HTTP_200_OK,
           summary="Actualiza los datos de un trabajador",
           responses={
               404: {"description": "Trabajador no encontrado"},
               400: {"description": "Datos inválidos para el tipo de trabajador"},
               200: {"description": "Trabajador actualizado correctamente"}
           })
async def modificar_trabajador(
    id_trabajador: int,
    datos: TrabajadorUpdate,
    db: Session = Depends(get_db)
) -> dict:
    """
    Actualiza los datos de un trabajador existente (comunes y específicos según su tipo).

    Args:
    - id_trabajador (int): ID del trabajador a modificar
    - datos (TrabajadorUpdate): Datos a actualizar
    - db (Session): Sesión de base de datos

    Returns:
    - dict: Mensaje de confirmación con ID del trabajador
    """
    # Buscar el trabajador principal
    trabajador = db.query(Trabajador).filter(Trabajador.id_trabajador == id_trabajador).first()
    if not trabajador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trabajador no encontrado"
        )

    # Actualizar campos comunes del trabajador
    campos_comunes = ['nombre', 'apellido1', 'apellido2', 'nombre_usuario', 'activo']
    update_data = datos.dict(exclude_unset=True, exclude={"cuidador_data", "gestor_data"})
    
    for campo in campos_comunes:
        if campo in update_data:
            setattr(trabajador, campo, update_data[campo])

    # Manejo de contraseña (si se proporciona)
    if 'contraseña' in update_data and update_data['contraseña']:
        trabajador.contraseña = update_data['contraseña']

    # Actualizar datos específicos según el tipo de trabajador
    if trabajador.cuidador and datos.cuidador_data:
        # Verificar que los datos de cuidador sean válidos
        if not isinstance(datos.cuidador_data, CuidadorData):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Datos de cuidador inválidos"
            )
        
        cuidador = trabajador.cuidador
        for campo, valor in datos.cuidador_data.dict(exclude_unset=True).items():
            setattr(cuidador, campo, valor)

    elif trabajador.gestor and datos.gestor_data:
        # Verificar que los datos de gestor sean válidos
        if not isinstance(datos.gestor_data, GestorData):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Datos de gestor inválidos"
            )
        
        gestor = trabajador.gestor
        for campo, valor in datos.gestor_data.dict(exclude_unset=True).items():
            setattr(gestor, campo, valor)

    try:
        db.commit()
        db.refresh(trabajador)
        return {
            "mensaje": "Trabajador actualizado correctamente",
            "id_trabajador": id_trabajador,
            "tipo": "cuidador" if trabajador.cuidador else "gestor"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el trabajador: {str(e)}"
        )
    

@router.post("/",
             response_model=dict,
             status_code=status.HTTP_201_CREATED,
             summary="Crea un nuevo trabajador, ya sea cuidador o gestor")
async def crear_trabajador(
    datos: TrabajadorUpdate,
    db: Session = Depends(get_db)
) -> dict:
    """
    Crea un nuevo trabajador, con datos comunes y específicos según tipo.

    Args:
    - datos (TrabajadorUpdate): Datos del nuevo trabajador
    - db (Session): Sesión de base de datos

    Returns:
    - dict: Mensaje de confirmación
    """
    try:
        trabajador = Trabajador(
            nombre=datos.nombre,
            apellido1=datos.apellido1,
            apellido2=datos.apellido2,
            nombre_usuario=datos.nombre_usuario,
            contraseña=datos.contraseña,
            activo=datos.activo if datos.activo is not None else True
        )
        db.add(trabajador)
        db.flush()  # Necesario para obtener el ID antes de añadir el rol

        tipo = None
        if datos.cuidador_data:
            cuidador = Cuidador(id_cuidador=trabajador.id_trabajador, **datos.cuidador_data.dict(exclude_unset=True))
            db.add(cuidador)
            tipo = "cuidador"
        elif datos.gestor_data:
            gestor = Gestor(id_gestor=trabajador.id_trabajador, **datos.gestor_data.dict(exclude_unset=True))
            db.add(gestor)
            tipo = "gestor"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe especificar los datos de cuidador o gestor"
            )

        db.commit()
        db.refresh(trabajador)

        return {
            "mensaje": "Trabajador creado correctamente",
            "id_trabajador": trabajador.id_trabajador,
            "tipo": tipo
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el trabajador: {str(e)}"
        )
