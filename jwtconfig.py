import jwt as jwt_module
from datetime import datetime, timedelta
import secrets

def generate_secret_key(length=32):
    return secrets.token_hex(length // 2)

# Ejemplo de uso
SECRET_KEY = generate_secret_key()
print("SECRET_KEY generada:", SECRET_KEY)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data.update({"exp": expire})
    encoded_jwt = jwt_module.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt_module.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt_module.ExpiredSignatureError:
        return None  # Token expirado
    except jwt_module.InvalidTokenError:
        return None  # Token inválido
