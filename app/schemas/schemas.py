from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from app.models.models import TaskStatus, TaskPriority

# ==========================================
# USER SCHEMAS
# ==========================================

class UserBase(BaseModel):
    """Campos comunes de User"""
    email: EmailStr
    nombre: str = Field(..., min_length=2, max_length=100)

class UserCreate(UserBase):
    """Schema para registrar usuario (recibe password en texto plano)"""
    password: str = Field(..., min_length=8)

class UserResponse(UserBase):
    """Schema para devolver usuario (SIN password_hash)"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True  # Permite convertir desde SQLAlchemy model

class UserLogin(BaseModel):
    """Schema para login"""
    email: EmailStr
    password: str

# ==========================================
# TASK SCHEMAS
# ==========================================

class TaskBase(BaseModel):
    """Campos comunes de Task"""
    titulo: str = Field(..., min_length=1, max_length=200)
    descripcion: Optional[str] = Field(None, max_length=1000)
    estado: TaskStatus
    prioridad: TaskPriority
    fecha_limite: Optional[datetime] = None

class TaskCreate(TaskBase):
    """Schema para crear tarea manualmente"""
    pass

class TaskCreateSmart(BaseModel):
    """Schema para crear tarea con IA (solo recibe texto)"""
    input: str = Field(..., min_length=5, max_length=500)

class TaskUpdate(BaseModel):
    """Schema para actualizar tarea (todos los campos opcionales)"""
    titulo: Optional[str] = Field(None, min_length=1, max_length=200)
    descripcion: Optional[str] = Field(None, max_length=1000)
    estado: Optional[TaskStatus] = None
    prioridad: Optional[TaskPriority] = None
    fecha_limite: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class TaskResponse(TaskBase):
    """Schema para devolver tarea"""
    id: int
    user_id: int
    original_input: Optional[str] = None
    created_by_ai: bool
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ==========================================
# AUTH SCHEMAS
# ==========================================

class Token(BaseModel):
    """Schema para respuesta de login"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse