import sys
from pathlib import Path
from datetime import datetime, date
from typing import Optional, List

from fastapi import FastAPI, Request, Depends, Form, Query, APIRouter, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from babel.dates import format_date
from fastapi.exception_handlers import http_exception_handler  # Importamos el manejador por defecto

# Importación de módulos internos
from app.dependencies.auth import require_login
from app.services.auth_service import verificar_usuario
from app.services.crud import create_horario
from app.database.db import SessionLocal, engine
from app.database.models import Base

# Importación de rutas
from app.routes import historico, cuidadores, hogares
from app.routes.dispositivos import detalle, zonas
from app.persons import clientes, data
from app.routes import verhorario
from app.routes.administracion.Cliente import Mod_Datos_Cliente
from app.routes.administracion.Hogar import Mod_datos_Hogar
from app.routes.administracion.Trabajador import Mod_Datos_Trabajador

# Añadir la raíz del proyecto al sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))


# Configuración inicial
BASE_DIR = Path(__file__).resolve().parent.parent
app = FastAPI()

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# Modelos
class HorarioCreate(BaseModel):
    id_cuidador: int
    id_cliente: int
    tipo_horario: str  # 'R' para Rango, 'I' para Individual
    fecha: Optional[str] = None
    fecha_inicio: Optional[str] = None
    fecha_fin: Optional[str] = None
    hora_inicio: str
    hora_fin: str
    color: Optional[str] = '#3498db'
    descripcion: Optional[str] = None
    parent_id: Optional[int] = None

    def transform_dates(self):
        if self.fecha:
            self.fecha = date.fromisoformat(self.fecha)
        if self.fecha_inicio:
            self.fecha_inicio = date.fromisoformat(self.fecha_inicio)
        if self.fecha_fin:
            self.fecha_fin = date.fromisoformat(self.fecha_fin)

# Dependencias de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Manejo de excepciones CORREGIDO
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    # Capturamos específicamente la excepción de redirección al login
    if exc.status_code == 307 and exc.detail == "Redirecting to login":
        return RedirectResponse(url="/login")
    # Para cualquier otra excepción HTTP, usamos el manejador por defecto
    return await http_exception_handler(request, exc)

# Registrar routers con protección de autenticación

api_router = APIRouter(dependencies=[Depends(require_login)])
api_router.include_router(data.router, prefix="/personas", tags=["Personas"])
api_router.include_router(historico.router, prefix="/historico", tags=["Historico"])
api_router.include_router(detalle.router, prefix="/dispositivos", tags=["Dispositivos"])
api_router.include_router(clientes.router, prefix="/personas", tags=["Clientes"])
api_router.include_router(zonas.router, prefix="/dispositivos", tags=["Zonas"])
api_router.include_router(cuidadores.router)
api_router.include_router(hogares.router)
api_router.include_router(verhorario.router)
api_router.include_router(Mod_Datos_Cliente.router)
api_router.include_router(Mod_datos_Hogar.router)
api_router.include_router(Mod_Datos_Trabajador.router)
app.include_router(api_router)


# Rutas principales
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
        datos_usuario = response["data"]

        if datos_usuario.get("fecha_nacimiento"):
            fecha_nac = datos_usuario["fecha_nacimiento"]
            hoy = datetime.utcnow().date()
            edad = (hoy - fecha_nac).days // 365
            datos_usuario["edad"] = edad
            fecha_formateada = format_date(fecha_nac, format='long', locale='es_ES')
            datos_usuario["fecha_nacimiento_es"] = fecha_formateada
        else:
            datos_usuario["edad"] = None
            datos_usuario["fecha_nacimiento_es"] = None

    except Exception as e:
        datos_usuario = None

    usuario_cookie = request.cookies.get("usuario", "")
    return templates.TemplateResponse("datos_sensor.html", {
        "request": request,
        "usuario": usuario_cookie,
        "datos": datos_usuario
    })

@app.get("/calendario", response_class=HTMLResponse)
async def calendario(request: Request, auth=Depends(require_login)):
    return templates.TemplateResponse("calendario.html", {"request": request})

@app.post("/guardar-horario/")
async def guardar_horario(
    horarios: List[HorarioCreate], 
    db: Session = Depends(get_db),
    auth=Depends(require_login)
):
    try:
        resultados = []
        for horario in horarios:
            horario.transform_dates()
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

# Rutas de autenticación (sin protección)
@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login_post(request: Request, usuario: str = Form(...), password: str = Form(...)):
    try:
        ok, rol = verificar_usuario(usuario, password)
        if ok and rol:
            response = RedirectResponse(url="/home", status_code=302)
            response.set_cookie(key="usuario", value=usuario)
            response.set_cookie(key="user_role", value=rol)
            return response
        else:
            return templates.TemplateResponse("login.html", {
                "request": request,
                "error": "Nombre de usuario o contraseña incorrectos"
            })
    except Exception as e:
        return PlainTextResponse(str(e), status_code=500)

@app.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("usuario")
    response.delete_cookie("user_role")
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)