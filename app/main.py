from fastapi import FastAPI
from app.persons import clientes, data
from app.routes import sensors, historico
from app.routes.dispositivos import detalle

app = FastAPI()


app.include_router(sensors.router, prefix="/sensors", tags=["Sensors"])
app.include_router(clientes.router, prefix="/persona", tags=["Persona"])
app.include_router(historico.router, prefix="/historico", tags=["Historico"])
app.include_router(detalle.router, prefix="/sensors/dispositivos", tags=["Dispositivos"])
app.include_router(data.router, prefix="/data", tags=["Token-Url,Persona"])


@app.get("/")
def root():
    return {"message": "Backend API funcionando"}
