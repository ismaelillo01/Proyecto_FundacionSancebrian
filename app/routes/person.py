from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

# Datos de prueba
persons_db = [
    {"id": 1, "name": "Ismael", "age": 20},
    {"id": 2, "name": "Laura", "age": 25},
    {"id": 3, "name": "Carlos", "age": 30},
]

@router.get("/persons")
def get_all_persons():
    return persons_db

@router.get("/persons/{person_id}")
def get_person(person_id: int):
    person = next((p for p in persons_db if p["id"] == person_id), None)
    if person:
        return person
    return JSONResponse(status_code=404, content={"error": "Persona no encontrada"})

@router.post("/persons")
def create_person(person: dict):
    persons_db.append(person)
    return {"message": "Persona creada", "person": person}
