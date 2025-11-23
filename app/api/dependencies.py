from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User
from app.services.auth_service import decode_access_token

# ==========================================
# OAUTH2 SCHEME
# ==========================================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# ==========================================
# DEPENDENCY: GET CURRENT USER
# ==========================================

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Dependency que extrae el usuario autenticado del JWT token.
    """
    payload= decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    email: str = payload.get("sub")
    
    user = db.query(User).filter(User.email == email).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    return user