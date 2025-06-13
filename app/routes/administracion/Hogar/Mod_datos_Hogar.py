from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from app.database.db import get_db
from app.database.models import Hogar
from app.models.user import HogarUpdate

router = APIRouter(
    prefix="/hogares",
    tags=["Hogares"],
    responses={404: {"description": "Hogar no encontrado"}}
)

@router.put(
    "/{hogar_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Actualiza los datos de un hogar",
    responses={
        200: {"description": "Datos del hogar actualizados correctamente"},
        404: {"description": "Hogar no encontrado"},
        400: {"description": "Datos de entrada inválidos"},
        500: {"description": "Error interno del servidor"}
    }
)
async def modificar_hogar(
    hogar_id: int,
    datos: HogarUpdate,
    db: Session = Depends(get_db)
) -> dict:
    """
    Actualiza los datos de un hogar existente.

    Args:
        hogar_id (int): ID del hogar a modificar
        datos (HogarUpdate): Datos a actualizar (solo los campos proporcionados serán modificados)
        db (Session): Sesión de base de datos

    Returns:
        dict: Mensaje de confirmación y datos básicos del hogar actualizado
    """
    # Buscar el hogar
    hogar = db.query(Hogar).filter(Hogar.id_hogar == hogar_id).first()
    if not hogar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hogar con ID {hogar_id} no encontrado"
        )

    # Campos permitidos para actualización
    campos_permitidos = [
        'url', 'token', 'direccion', 
        'codigo_postal', 'provincia', 'activo'
    ]

    # Filtrar solo los campos permitidos y que tienen valor
    update_data = datos.dict(exclude_unset=True)
    campos_actualizados = []
    
    try:
        for campo in campos_permitidos:
            if campo in update_data:
                # Validación adicional para campos específicos si es necesario
                if campo == 'codigo_postal' and update_data[campo]:
                    if len(update_data[campo]) != 5 or not update_data[campo].isdigit():
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="El código postal debe tener 5 dígitos"
                        )
                
                setattr(hogar, campo, update_data[campo])
                campos_actualizados.append(campo)

        db.commit()
        db.refresh(hogar)

        return {
            "mensaje": "Hogar actualizado correctamente",
            "hogar_id": hogar.id_hogar,
            "campos_actualizados": campos_actualizados,
            "direccion": hogar.direccion,
            "activo": hogar.activo
        }

    except ValueError as ve:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Datos inválidos: {str(ve)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el hogar: {str(e)}"
        )
    


@router.post("/",
             response_model=dict,
             status_code=status.HTTP_201_CREATED,
             summary="Crea un nuevo hogar")
async def crear_hogar(
    datos: HogarUpdate,
    db: Session = Depends(get_db)
) -> dict:
    """
    Crea un nuevo hogar con los datos proporcionados.

    Args:
    - datos (HogarUpdate): Datos del nuevo hogar
    - db (Session): Sesión de base de datos

    Returns:
    - dict: Mensaje de confirmación
    """
    try:
        if datos.codigo_postal and (len(datos.codigo_postal) != 5 or not datos.codigo_postal.isdigit()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El código postal debe tener 5 dígitos"
            )

        nuevo_hogar = Hogar(
            url=datos.url,
            token=datos.token,
            direccion=datos.direccion,
            codigo_postal=datos.codigo_postal,
            provincia=datos.provincia,
            activo=datos.activo if datos.activo is not None else True
        )
        db.add(nuevo_hogar)
        db.commit()
        db.refresh(nuevo_hogar)

        return {
            "mensaje": "Hogar creado correctamente",
            "hogar_id": nuevo_hogar.id_hogar
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el hogar: {str(e)}"
        )
