from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.database import get_db
from app.services.gemini_service import extract_task_data, suggest_next_task
from app.schemas.schemas import TaskCreate, TaskUpdate, TaskResponse, TaskCreateSmart
from app.models.models import User, Task, TaskStatus, TaskPriority
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])

# ==========================================
# GET /tasks - Listar tareas
# ==========================================
@router.get("/", response_model=list[TaskResponse])
def get_tasks(
    estado: Optional[TaskStatus] = Query(None, description="Filtrar por estado"),
    prioridad: Optional[TaskPriority] = Query(None, description="Filtrar por prioridad"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista todas las tareas del usuario autenticado.
    
    Permite filtrar por:
    - estado: pending, in_progress, completed, cancelled
    - prioridad: low, medium, high, urgent
    
    Args:
        estado: Filtro opcional por estado
        prioridad: Filtro opcional por prioridad
        db: Sesión de BD
        current_user: Usuario autenticado
        
    Returns:
        Lista de tareas del usuario
    """
    
    query = db.query(Task).filter(Task.user_id == current_user.id)
    
    if estado:
        query = query.filter(Task.estado == estado)
    
    if prioridad:
        query = query.filter(Task.prioridad == prioridad)
    
    query = query.order_by(Task.fecha_limite.asc().nullslast())
    
    tasks = query.all()
    return tasks

# ==========================================
# POST /tasks - Crear tarea manual
# ==========================================
@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crea una nueva tarea manualmente.
    
    Args:
        task_data: Datos de la tarea (título, descripción, fecha_límite, prioridad)
        db: Sesión de BD
        current_user: Usuario autenticado
        
    Returns:
        Tarea creada
    """
    new_task = Task(
        user_id=current_user.id,
        titulo=task_data.titulo,
        descripcion=task_data.descripcion,
        estado=TaskStatus.PENDING,
        prioridad=task_data.prioridad,
        fecha_limite=task_data.fecha_limite,
        created_by_ai=False
    )
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    return new_task

# ==========================================
# GET /tasks/{id} - Ver tarea específica
# ==========================================
@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene una tarea específica por su ID.
    
    Args:
        task_id: ID de la tarea
        db: Sesión de BD
        current_user: Usuario autenticado
        
    Returns:
        Tarea solicitada
        
    Raises:
        HTTPException 404: Si la tarea no existe o no pertenece al usuario
    """
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )
    
    return task

# ==========================================
# PUT /tasks/{id} - Actualizar tarea
# ==========================================
@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Actualiza una tarea existente.
    
    Solo actualiza los campos proporcionados (partial update).
    
    Args:
        task_id: ID de la tarea a actualizar
        task_data: Datos actualizados de la tarea
        db: Sesión de BD
        current_user: Usuario autenticado
        
    Returns:
        Tarea actualizada
        
    Raises:
        HTTPException 404: Si la tarea no existe o no pertenece al usuario
    """
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )
    
    update_data = task_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    
    return task

# ==========================================
# DELETE /tasks/{id} - Eliminar tarea
# ==========================================
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Elimina una tarea.
    
    Args:
        task_id: ID de la tarea
        db: Sesión de BD
        current_user: Usuario autenticado
        
    Raises:
        HTTPException 404: Si la tarea no existe
    """
    
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )
    
    db.delete(task)
    db.commit()
    
    return None

# ==========================================
# PATCH /tasks/{id}/complete
# ==========================================
@router.patch("/{task_id}/complete", response_model=TaskResponse)
def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Marca una tarea como completada.
    
    Actualiza:
    - estado = COMPLETED
    - completed_at = now()
    
    Args:
        task_id: ID de la tarea
        db: Sesión de BD
        current_user: Usuario autenticado
        
    Returns:
        Tarea completada
        
    Raises:
        HTTPException 404: Si la tarea no existe
        HTTPException 400: Si la tarea ya está completada
    """
    
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )
    
    if task.estado == TaskStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La tarea ya está completada"
        )
    
    task.estado = TaskStatus.COMPLETED
    task.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(task)
    
    return task


# ==========================================
# POST /tasks/create-smart - Crear con IA
# ==========================================

@router.post("/create-smart", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task_smart(
    smart_data: TaskCreateSmart,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crea una tarea usando IA para extraer datos desde lenguaje natural.
    
    Ejemplo:
        Input: "Llamar al dentista mañana a las 10am, es urgente"
        → Gemini extrae: titulo, descripcion, fecha_limite, prioridad
        → Se crea la tarea automáticamente
    
    Args:
        smart_data: Solo contiene "input" (texto del usuario)
        db: Sesión de BD
        current_user: Usuario autenticado
        
    Returns:
        Tarea creada con IA
        
    Raises:
        HTTPException 400: Si Gemini no puede procesar el texto
    """
    
    try:
        extracted_data = extract_task_data(smart_data.input)
        
        new_task = Task(
            user_id=current_user.id,
            titulo=extracted_data["titulo"],
            descripcion=extracted_data.get("descripcion"),
            estado=TaskStatus.PENDING,
            prioridad=extracted_data["prioridad"],
            fecha_limite=extracted_data.get("fecha_limite"),
            original_input=smart_data.input,
            created_by_ai=True
        )
        
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        
        return new_task
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No pude procesar tu solicitud: {str(e)}"
        )
    except Exception as e:
        # Error inesperado
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )


# ==========================================
# POST /tasks/suggest-next - Sugerir acción
# ==========================================

@router.post("/suggest-next")
def suggest_next_action(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Usa IA para sugerir qué tarea hacer ahora.
    
    Analiza todas las tareas del usuario y recomienda la más apropiada
    según prioridad, fecha límite y estado.
    
    Args:
        db: Sesión de BD
        current_user: Usuario autenticado
        
    Returns:
        {
          "sugerencia": "Deberías completar X porque...",
          "task_id": 123,
          "task": {...}  # Datos de la tarea sugerida
        }
    """
    
    tasks = db.query(Task).filter(Task.user_id == current_user.id).all()
    
    tasks_dicts = [
        {
            "id": task.id,
            "titulo": task.titulo,
            "estado": task.estado.value,
            "prioridad": task.prioridad.value,
            "fecha_limite": task.fecha_limite,
        }
        for task in tasks
    ]
    
    suggestion = suggest_next_task(tasks_dicts)
    
    suggested_task = None
    if suggestion["task_id"]:
        suggested_task = db.query(Task).filter(
            Task.id == suggestion["task_id"],
            Task.user_id == current_user.id
        ).first()
    
    return {
        "sugerencia": suggestion["sugerencia"],
        "task_id": suggestion["task_id"],
        "task": TaskResponse.model_validate(suggested_task) if suggested_task else None
    }