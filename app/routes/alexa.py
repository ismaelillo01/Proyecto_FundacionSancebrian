from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/alexa")
async def alexa_get():
    return {"message": "Ruta Alexa activa y escuchando"}

@router.post("/alexa")
async def handle_alexa_request(request: Request):
    body = await request.json()
    print("Alexa Request:", body)

    # Respuesta mínima válida para Alexa
    return {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": "Hola, tu skill está funcionando correctamente."
            },
            "shouldEndSession": False
        }
    }
