import sys
from pathlib import Path

from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.dependencies.auth import require_login
from app.services.auth_service import verificar_usuario
from app.routes import sensors, historico
from app.routes.dispositivos import detalle
from app.persons import clientes, data
from fastapi.responses import RedirectResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

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
@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login_post(request: Request, usuario: str = Form(...), password: str = Form(...)):
    if verificar_usuario(usuario, password):
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(key="usuario", value=usuario)
        return response
    else:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Nombre de usuario o contraseña incorrectos"
        })
    
@app.get("/datos", response_class=HTMLResponse, name="datos_sensor")
async def datos(request: Request, auth=Depends(require_login)):
    return templates.TemplateResponse("datos_sensor.html", {"request": request, "usuario": usuario})


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
