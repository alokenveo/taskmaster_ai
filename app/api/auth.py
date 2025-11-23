from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.schemas import UserCreate, UserResponse, UserLogin, Token
from app.models.models import User
from app.services.auth_service import hash_password, verify_password, create_access_token
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ==========================================
# POST /auth/register
# ==========================================
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario.
    
    Args:
        user_data: Datos del usuario (email, password, nombre)
        db: Sesión de BD
        
    Returns:
        Usuario creado (sin password_hash)
        
    Raises:
        HTTPException 400: Si el email ya está registrado
    """
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    hashed_password = hash_password(user_data.password)
    
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        nombre=user_data.nombre
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

# ==========================================
# POST /auth/login
# ==========================================
@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Autentica a un usuario y genera un token JWT.
    
    Args:
        credentials: Credenciales de login (email, password)
        db: Sesión de BD
        
    Returns:
        Token JWT y datos del usuario
        
    Raises:
        HTTPException 401: Si las credenciales son inválidas
    """
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o password incorrectos",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    access_token = create_access_token(data={"sub": user.email})
    
    return {"access_token": access_token, "token_type": "bearer", "user": user}

# ==========================================
# GET /auth/me
# ==========================================
@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Obtiene los datos del usuario autenticado.
    
    Este endpoint sirve para:
    - Verificar que el token es válido
    - Obtener datos actualizados del usuario
    - Testing de autenticación
    
    Args:
        current_user: Usuario autenticado (extraído del token)
    Returns:
        Datos del usuario autenticado
    """
    return current_user