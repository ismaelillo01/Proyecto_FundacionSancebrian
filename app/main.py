from fastapi import FastAPI
from app.routes import auth, sensors ,person  

app = FastAPI()

# Incluir routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(sensors.router, prefix="/sensors", tags=["Sensors"])

@app.get("/")
def root():
    return {"message": "Backend API funcionando"}
