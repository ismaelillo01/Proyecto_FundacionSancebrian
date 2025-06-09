#!/bin/bash

# Ir al directorio del proyecto
cd /mnt/c/Users/Propietario/Proyecto_FundacionSancebrian || exit

# Activar entorno virtual
source venv/bin/activate

# Lanzar el servidor con Gunicorn + UvicornWorker
gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000

