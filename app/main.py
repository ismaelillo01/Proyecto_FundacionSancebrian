from fastapi import FastAPI
from app.routes import sensors, person, historico

app = FastAPI()

# Incluir routers
app.include_router(sensors.router, prefix="/sensors", tags=["Sensors"])
app.include_router(person.router, prefix="/person", tags=["Person"])
app.include_router(historico.router, prefix="/historico", tags=["Historico"])


@app.get("/")
def root():
    return {"message": "Backend API funcionando"}
