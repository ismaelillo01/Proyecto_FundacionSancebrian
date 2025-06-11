import sys
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, Request, Depends, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from babel.dates import format_date

# Importación de módulos internos
from app.dependencies.auth import require_login
from app.services.auth_service import verificar_usuario
from app.services.crud import create_horario
from app.database.db import SessionLocal, engine
from app.database.models import Base
from typing import Optional
from typing import List
# Importación de rutas
from app.routes import historico, alexa, cuidadores, hogares
from app.routes.dispositivos import detalle, zonas
from app.persons import clientes, data
from app.database.models import Horario, Cuidador, Cliente

# Añadir la raíz del proyecto al sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))


# app/main.py
from pydantic import BaseModel
from typing import Optional
from datetime import date


class HorarioCreate(BaseModel):
    id_cuidador: int
    id_cliente: int
    tipo_horario: str  # 'R' para Rango, 'I' para Individual
    fecha: Optional[str] = None  # La fecha es opcional, puede ser None
    fecha_inicio: Optional[str] = None  # También opcional
    fecha_fin: Optional[str] = None  # También opcional
    hora_inicio: str
    hora_fin: str
    color: Optional[str] = '#3498db'  # Opcional, por defecto '#3498db'
    descripcion: Optional[str] = None  # Opcional
    parent_id: Optional[int] = None  # Opcional, puede ser None

    # Función para convertir las fechas de string a tipo Date
    def transform_dates(self):
        if self.fecha:
            self.fecha = date.fromisoformat(self.fecha)
        if self.fecha_inicio:
            self.fecha_inicio = date.fromisoformat(self.fecha_inicio)
        if self.fecha_fin:
            self.fecha_fin = date.fromisoformat(self.fecha_fin)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()




@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 307 and exc.detail == "Redirecting to login":
        return RedirectResponse(url="/login")
    raise exc


# Ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Montaje de archivos estáticos
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# Plantillas
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# Registrar routers
app.include_router(data.router, prefix="/personas", tags=["Personas"])
app.include_router(historico.router, prefix="/historico", tags=["Historico"])
app.include_router(detalle.router, prefix="/dispositivos", tags=["Dispositivos"])
app.include_router(clientes.router, prefix="/personas", tags=["Clientes"])
app.include_router(zonas.router, prefix="/dispositivos", tags=["Zonas"])
app.include_router(alexa.router)
app.include_router(cuidadores.router)
app.include_router(hogares.router)

# Rutas protegidas
@app.get("/", response_class=HTMLResponse)
async def root(request: Request, auth=Depends(require_login)):
    usuario = request.cookies.get("usuario", "")
    rol = request.cookies.get("user_role", "cuidador")
    return templates.TemplateResponse("index.html", {"request": request, "usuario": usuario, "user_role": rol})

@app.get("/home", response_class=HTMLResponse)
async def home(request: Request, auth=Depends(require_login)):
    usuario = request.cookies.get("usuario", "")
    rol = request.cookies.get("user_role", "cuidador")
    return templates.TemplateResponse("index.html", {"request": request, "usuario": usuario, "user_role": rol})

@app.post("/login", response_class=HTMLResponse)
async def login_post(request: Request, usuario: str = Form(...), password: str = Form(...)):
    try:
        ok, rol = verificar_usuario(usuario, password)
        if ok and rol:
            response = RedirectResponse(url="/home", status_code=302)
            response.set_cookie(key="usuario", value=usuario)
            response.set_cookie(key="user_role", value=rol)
            print(f"[DEBUG] Usuario {usuario} autenticado como {rol}")
            return response
        else:
            return templates.TemplateResponse("login.html", {
                "request": request,
                "error": "Nombre de usuario o contraseña incorrectos"
            })
    except Exception as e:
        return PlainTextResponse(str(e), status_code=500)

@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("usuario")
    response.delete_cookie("user_role")
    return response

@app.get("/miportal", response_class=HTMLResponse, name="miportal")
async def mi_portal(request: Request, auth=Depends(require_login)):
    usuario = request.cookies.get("usuario", "")
    role = request.cookies.get("user_role", "cuidador")
    return templates.TemplateResponse("MiPortal.html", {"request": request, "usuario": usuario, "role": role})
@app.get("/datos", response_class=HTMLResponse, name="datos_sensor")
async def datos(request: Request, usuario_id: int = Query(...), auth=Depends(require_login)):
    from app.persons.clientes import get_cliente_detalle

    try:
        response = get_cliente_detalle(usuario_id)
        print(">>> Datos del cliente:", response)
        datos_usuario = response["data"]

        # ➕ Calcular edad si hay fecha de nacimiento
        if datos_usuario.get("fecha_nacimiento"):
            fecha_nac = datos_usuario["fecha_nacimiento"]
            hoy = datetime.utcnow().date()
            edad = (hoy - fecha_nac).days // 365
            datos_usuario["edad"] = edad

            # 🗓️ Formatear fecha en español
            fecha_formateada = format_date(fecha_nac, format='long', locale='es_ES')
            datos_usuario["fecha_nacimiento_es"] = fecha_formateada
        else:
            datos_usuario["edad"] = None
            datos_usuario["fecha_nacimiento_es"] = None

    except Exception as e:
        print(">>> ERROR:", str(e))
        datos_usuario = None

    usuario_cookie = request.cookies.get("usuario", "")
    return templates.TemplateResponse("datos_sensor.html", {
        "request": request,
        "usuario": usuario_cookie,
        "datos": datos_usuario
    })

@app.get("/calendario", response_class=HTMLResponse)
async def calendario(request: Request):
    return templates.TemplateResponse("calendario.html", {"request": request})

@app.post("/guardar-horario/")
async def guardar_horario(horarios: List[HorarioCreate], db: Session = Depends(get_db)):
    try:
        resultados = []
        for horario in horarios:
            horario.transform_dates()  # Asegura que las fechas sean convertidas
            horario_data = horario.dict()
            new_horario = create_horario(db=db, horario_data=horario_data)
            resultados.append(new_horario.dict())

        return JSONResponse(
            content={"message": "Horarios guardados exitosamente", "count": len(resultados), "data": resultados},
            status_code=200
        )

    except Exception as e:
        return JSONResponse(
            content={"message": "Error al guardar horarios", "error": str(e)},
            status_code=400
        )



# Ejecutar como script
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

