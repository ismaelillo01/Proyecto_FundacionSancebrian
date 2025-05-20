from app.core.security import hash_password

users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": hash_password("123")  # ← hash generado en tiempo de ejecución
    }
}

def get_user(username: str):
    return users_db.get(username)
