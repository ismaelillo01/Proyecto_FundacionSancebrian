#app/routes/administracion/cliente/Mod_Datos_Cliente.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date
from app.database.db import get_db
from app.database.models import Cliente, DatosCliente
from app.models.user import ClienteUpdate
from app.models.user import ClienteCreate 

router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"]
)

@router.put("/{id_cliente}", 
           response_model=dict,
           status_code=status.HTTP_200_OK,
           summary="Actualiza los datos de un cliente",
           responses={
               404: {"description": "Cliente no encontrado"},
               200: {"description": "Datos del cliente actualizados correctamente"}
           })
async def modificar_cliente(
    id_cliente: int, 
    datos: ClienteUpdate, 
    db: Session = Depends(get_db)
) -> dict:
    """
    Actualiza los datos de un cliente existente.

    Args:
    - id_cliente (int): ID del cliente a modificar
    - datos (ClienteUpdate): Datos a actualizar
    - db (Session): Sesión de base de datos

    Returns:
    - dict: Mensaje de confirmación
    """
    # Buscar el cliente principal
    cliente = db.query(Cliente).filter(Cliente.id_cliente == id_cliente).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )

    # Actualizar campos en la tabla Cliente si están presentes en los datos
    cliente_fields = ['activo']
    for field in cliente_fields:
        if field in datos.dict(exclude_unset=True):
            setattr(cliente, field, getattr(datos, field))

    # Actualizar campos en DatosCliente
    datos_personales = cliente.datos_personales
    if not datos_personales:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Datos personales del cliente no encontrados"
        )

    # Campos que pertenecen a DatosCliente
    datos_cliente_fields = [
        'nombre', 'apellido1', 'apellido2', 'dni', 'sexo', 
        'descripcion', 'fecha_nacimiento', 'telefono_contacto',
        'telefono_familiar', 'email'
    ]

    update_data = datos.dict(exclude_unset=True)
    for field in datos_cliente_fields:
        if field in update_data:
            # Manejo especial para fechas (si es necesario)
            if field == 'fecha_nacimiento' and update_data[field] is not None:
                if isinstance(update_data[field], str):
                    update_data[field] = date.fromisoformat(update_data[field])
            setattr(datos_personales, field, update_data[field])

    try:
        db.commit()
        db.refresh(cliente)
        return {
            "mensaje": "Cliente actualizado correctamente",
            "id_cliente": id_cliente
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el cliente: {str(e)}"
        )
    
    


@router.post("/", 
             response_model=dict,
             status_code=status.HTTP_201_CREATED,
             summary="Crea un nuevo cliente con sus datos personales")
async def crear_cliente(
    datos: ClienteCreate,
    db: Session = Depends(get_db)
) -> dict:
    """
    Crea un nuevo cliente con sus datos personales.

    Args:
    - datos (ClienteCreate): Datos del nuevo cliente
    - db (Session): Sesión de base de datos

    Returns:
    - dict: Mensaje de confirmación
    """
    try:
        cliente = Cliente(
            id_hogar=datos.id_hogar,
            id_gestor=datos.id_gestor,
            activo=datos.activo if datos.activo is not None else True
        )
        db.add(cliente)
        db.flush()  # Obtener id_cliente generado por autoincrement

        datos_personales = DatosCliente(
            id_cliente=cliente.id_cliente,
            nombre=datos.nombre,
            apellido1=datos.apellido1,
            apellido2=datos.apellido2,
            dni=datos.dni,
            sexo=datos.sexo,
            descripcion=datos.descripcion,
            fecha_nacimiento=datos.fecha_nacimiento,
            telefono_contacto=datos.telefono_contacto,
            telefono_familiar=datos.telefono_familiar,
            email=datos.email
        )
        db.add(datos_personales)
        db.commit()
        db.refresh(cliente)

        return {
            "mensaje": "Cliente creado correctamente",
            "id_cliente": cliente.id_cliente
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el cliente: {str(e)}"
        )
