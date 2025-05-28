from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from app.services.auth_service import verify_user_credentials

router = APIRouter()

@router.get("/login", response_class=HTMLResponse)
def login_get(request: Request):
    return request.app.state.templates.TemplateResponse("login.html", {"request": request})

@router.post("/login", response_class=HTMLResponse)
async def login_post(
    request: Request,
    usuario: str = Form(...),
    password: str = Form(...)
):
    if verify_user_credentials(usuario, password):
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(key="logged_in", value="true", httponly=True)
        response.set_cookie(key="usuario", value=usuario)
        return response
    else:
        return request.app.state.templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Credenciales incorrectas"
        })

@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("logged_in")
    response.delete_cookie("usuario")
    return response
