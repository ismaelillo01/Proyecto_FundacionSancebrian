from pydantic import BaseModel

class UserLogin(BaseModel):
    usuario: str
    password: str
