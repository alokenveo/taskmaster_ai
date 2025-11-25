from fastapi import FastAPI
from app.database import Base, engine
from app.models import models
from app.api import auth, tasks

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TaskMaster AI",
    description="Sistema de gestión de tareas con asistente IA",
    version="1.0.0"
)

# ==========================================
# REGISTRAR ROUTERS
# ==========================================
app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/")
def root():
    return {
        "message": "¡Bienvenido a TaskMaster AI!",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}