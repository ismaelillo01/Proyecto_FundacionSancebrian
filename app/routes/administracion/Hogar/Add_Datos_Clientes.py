@router.post("/", 
             response_model=dict,
             status_code=status.HTTP_201_CREATED,
             summary="Crea un nuevo cliente con sus datos personales")
async def crear_cliente(
    datos: ClienteUpdate,
    db: Session = Depends(get_db)
) -> dict:
    """
    Crea un nuevo cliente con sus datos personales.

    Args:
    - datos (ClienteUpdate): Datos del nuevo cliente
    - db (Session): Sesión de base de datos

    Returns:
    - dict: Mensaje de confirmación
    """
    try:
        cliente = Cliente(activo=datos.activo if datos.activo is not None else True)
        db.add(cliente)
        db.flush()  # para obtener el ID antes de añadir datos_personales

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
