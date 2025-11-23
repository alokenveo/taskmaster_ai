from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

# ==========================================
# CONFIGURACIÓN
# ==========================================

# CryptContext gestiona el hashing de passwords con bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ==========================================
# FUNCIONES DE PASSWORD
# ==========================================

def hash_password(password: str) -> str:
    """
    Convierte password en texto plano a hash bcrypt.
    """
    
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si un password coincide con su hash.
    """
    return pwd_context.verify(plain_password, hashed_password)


# ==========================================
# FUNCIONES DE JWT
# ==========================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un JWT token.
    """
    to_encode = data.copy()
    
    # Calcular expiración
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    # Añadir claim de expiración
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodifica y valida un JWT token.
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None