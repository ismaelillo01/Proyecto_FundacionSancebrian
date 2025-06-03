import sys
from pathlib import Path

from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Query
from app.dependencies.auth import require_login
from app.services.auth_service import verificar_usuario
from app.routes import sensors, historico
from app.routes.dispositivos import detalle
from app.persons import clientes, data
from fastapi.responses import RedirectResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.routes.dispositivos import zonas
from datetime import datetime
from babel.dates import format_date
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI






# Añadir la raíz del proyecto al sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Crear instancia FastAPI
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
app.include_router(sensors.router, prefix="/sensors", tags=["Sensors"])
app.include_router(data.router, prefix="/personas", tags=["Personas"])
app.include_router(historico.router, prefix="/historico", tags=["Historico"])
app.include_router(detalle.router, prefix="/dispositivos", tags=["Dispositivos"])
app.include_router(clientes.router, prefix="/personas", tags=["Clientes"])
app.include_router(zonas.router, prefix="/dispositivos", tags=["Zonas"])

# Rutas protegidas
@app.get("/", response_class=HTMLResponse)
async def root(request: Request, auth=Depends(require_login)):
    usuario = request.cookies.get("usuario", "")
    return templates.TemplateResponse("index.html", {"request": request, "usuario": usuario})

@app.get("/home", response_class=HTMLResponse)
async def home(request: Request, auth=Depends(require_login)):
    usuario = request.cookies.get("usuario", "")
    return templates.TemplateResponse("index.html", {"request": request, "usuario": usuario})

# Login
@app.get("/home", response_class=HTMLResponse)
async def home(request: Request, auth=Depends(require_login)):
    usuario = request.cookies.get("usuario", "")
    return templates.TemplateResponse("index.html", {"request": request, "usuario": usuario})


from fastapi.responses import PlainTextResponse

@app.post("/login", response_class=HTMLResponse)
async def login_post(request: Request, usuario: str = Form(...), password: str = Form(...)):
    try:
        if verificar_usuario(usuario, password):
            response = RedirectResponse(url="/home", status_code=302)
            response.set_cookie(key="usuario", value=usuario)
            return response
        else:
            return templates.TemplateResponse("login.html", {
                "request": request,
                "error": "Nombre de usuario o contraseña incorrectos"
            })
    except Exception as e:
        # Mostrar error como texto plano para debug
        return PlainTextResponse(str(e), status_code=500)



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
            edad = (hoy - fecha_nac.date()).days // 365
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



app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # o ["*"] si quieres probar rápido
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Logout
@app.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("usuario")
    return response



# Ejecutar como script
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

@app.get("/miportal", response_class=HTMLResponse, name="miportal")
async def mi_portal(request: Request, auth=Depends(require_login)):
    usuario = request.cookies.get("usuario", "")
    return templates.TemplateResponse("MiPortal.html", {"request": request, "usuario": usuario})
