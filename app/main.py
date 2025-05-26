from fastapi import FastAPI
from app.routes import sensors, historico
from app.routes.dispositivos import detalle
from app.persons import data  # tu router de personas (clientes)

app = FastAPI()

app.include_router(sensors.router, prefix="/sensors", tags=["Sensors"])
app.include_router(data.router, prefix="/personas", tags=["Personas"])  # Aquí personas con prefijo coherente
app.include_router(historico.router, prefix="/historico", tags=["Historico"])
app.include_router(detalle.router, prefix="/dispositivos", tags=["Dispositivos"])  # Mejor sin subprefixo "/sensors/dispositivos"
# Evitar redundancias en URL y facilitar frontend

@app.get("/")
def root():
    return {"message": "Backend API funcionando"}
