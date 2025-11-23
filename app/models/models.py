from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


# ==========================================
# ENUMS (Python)
# ==========================================
class TaskStatus(str, enum.Enum):
    """Estados posibles de una tarea"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, enum.Enum):
    """Prioridades de tareas"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# ==========================================
# MODELO: User
# ==========================================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nombre = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")


# ==========================================
# MODELO: Task
# ==========================================
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    estado = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    prioridad = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    fecha_limite = Column(DateTime, nullable=True)
    original_input = Column(Text, nullable=True)
    created_by_ai = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("idx_tasks_user_estado", "user_id", "estado"),
        Index("idx_tasks_fecha_limite", "fecha_limite"),
    )

    owner = relationship("User", back_populates="tasks")
