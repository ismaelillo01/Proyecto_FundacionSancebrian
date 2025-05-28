from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse

def require_login(request: Request):
    usuario = request.cookies.get("usuario")
    if not usuario:
        raise HTTPException(status_code=307, detail="Redirecting to login")
