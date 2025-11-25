# 🤖 TaskMaster AI

API REST inteligente para gestión de tareas con procesamiento de lenguaje natural powered by Gemini AI.

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.121-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)

## 🌟 Features

- ✅ **Autenticación JWT** - Sistema seguro de registro y login
- 🤖 **Inteligencia Artificial** - Crea tareas desde lenguaje natural ("Reunión con María mañana 3pm")
- 📊 **CRUD completo** - Gestión completa de tareas con filtros y búsqueda
- 🎯 **Recomendaciones inteligentes** - La IA sugiere qué tarea hacer ahora
- 🔒 **Seguridad** - Passwords hasheados con bcrypt, tokens JWT
- 📚 **Documentación automática** - Swagger UI interactiva
- 🧪 **Testing automatizado** - Suite de tests con pytest
<!-- - ☁️ **Cloud-ready** - Deployado en Render con PostgreSQL 

## 🚀 Demo en vivo

🔗 **API**: [https://taskmaster-ai-xxxx.onrender.com](https://taskmaster-ai-xxxx.onrender.com)  
📖 **Documentación**: [https://taskmaster-ai-xxxx.onrender.com/docs](https://taskmaster-ai-xxxx.onrender.com/docs)

> **Nota**: Reemplaza `xxxx` con tu URL real de Render

-->

## 📸 Screenshots

### Crear tarea con IA (lenguaje natural)
```json
POST /tasks/create-smart
{
  "input": "Llamar al dentista mañana a las 10am, es urgente"
}

// La IA extrae automáticamente:
✅ Título: "Llamar al dentista"
✅ Fecha: 2024-11-24T10:00:00
✅ Prioridad: urgent
```

### Sugerencia inteligente
```json
POST /tasks/suggest-next

// Respuesta:
{
  "sugerencia": "Te recomiendo completar 'Llamar al dentista' porque vence en 2 horas y es urgente",
  "task_id": 123
}
```

## 🏗️ Arquitectura
```
taskmaster-ai/
├── app/
│   ├── main.py              # Punto de entrada FastAPI
│   ├── config.py            # Configuración y variables de entorno
│   ├── database.py          # Conexión PostgreSQL
│   ├── models/
│   │   └── models.py        # Modelos SQLAlchemy (User, Task)
│   ├── schemas/
│   │   └── schemas.py       # Schemas Pydantic (validación)
│   ├── api/
│   │   ├── auth.py          # Endpoints autenticación
│   │   ├── tasks.py         # Endpoints tareas
│   │   └── dependencies.py  # Dependency injection
│   └── services/
│       ├── auth_service.py  # Lógica auth (JWT, bcrypt)
│       └── gemini_service.py # Integración Gemini AI
├── tests/
│   └── test_auth.py         # Tests automatizados
├── requirements.txt
├── render.yaml              # Configuración deploy
└── README.md
```

### Stack tecnológico

**Backend**:
- **FastAPI** - Framework web async moderno
- **SQLAlchemy** - ORM para PostgreSQL
- **Pydantic** - Validación de datos
- **PostgreSQL** - Base de datos relacional

**Autenticación**:
- **python-jose** - JWT tokens
- **passlib + bcrypt** - Hashing de passwords

**Inteligencia Artificial**:
- **Google Gemini 2.5 Flash** - Procesamiento de lenguaje natural
- Extracción de datos estructurados desde texto
- Sistema de recomendaciones

**Testing & Deploy**:
- **pytest** - Testing automatizado
- **Render** - Hosting y CI/CD
<!-- - **Render PostgreSQL** - Base de datos en la nube -->

## 🛠️ Instalación local

### Requisitos previos
- Python 3.13+
- PostgreSQL 15+
- API Key de Gemini ([obtener aquí](https://aistudio.google.com/app/apikey))

### Pasos

1. **Clonar el repositorio**
```bash
git clone https://github.com/alokenveo/taskmaster-ai.git
cd taskmaster-ai
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**

Crear archivo `.env` en la raíz:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/taskmaster_db
SECRET_KEY=tu-secret-key-super-segura-cambiala
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
GEMINI_API_KEY=tu-gemini-api-key
ENVIRONMENT=development
```

5. **Crear base de datos**
```bash
# En PostgreSQL
createdb taskmaster_db
```

6. **Ejecutar la aplicación**
```bash
uvicorn app.main:app --reload
```

7. **Acceder a la documentación**

Abre tu navegador en: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## 🧪 Testing

Ejecutar todos los tests:
```bash
pytest tests/ -v
```

Ejecutar tests con coverage:
```bash
pytest tests/ --cov=app --cov-report=html
```

Ver coverage en navegador:
```bash
open htmlcov/index.html
```

## 📡 API Endpoints

### Autenticación
```http
POST   /auth/register     # Registrar nuevo usuario
POST   /auth/login        # Login y obtener JWT token
GET    /auth/me           # Obtener usuario actual
```

### Tareas (requieren autenticación)
```http
GET    /tasks                    # Listar tareas (con filtros opcionales)
POST   /tasks                    # Crear tarea manual
GET    /tasks/{id}               # Obtener tarea específica
PUT    /tasks/{id}               # Actualizar tarea
PATCH  /tasks/{id}/complete      # Marcar como completada
DELETE /tasks/{id}               # Eliminar tarea
```

### Inteligencia Artificial
```http
POST   /tasks/create-smart       # Crear tarea desde lenguaje natural
POST   /tasks/suggest-next       # Obtener sugerencia de qué hacer
```

### Ejemplos de uso

#### Registrar usuario
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "nombre": "John Doe"
  }'
```

#### Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

#### Crear tarea con IA
```bash
curl -X POST "http://localhost:8000/tasks/create-smart" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Reunión con el equipo el próximo martes a las 10am"
  }'
```

#### Listar tareas pendientes urgentes
```bash
curl -X GET "http://localhost:8000/tasks?estado=pending&prioridad=urgent" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🤖 Cómo funciona la IA

### Extracción de datos (create-smart)

1. **Usuario escribe en lenguaje natural**:
```
   "Llamar a Juan mañana a las 3pm para revisar el presupuesto, es importante"
```

2. **Gemini analiza y extrae**:
   - **Título**: "Llamar a Juan"
   - **Descripción**: "Revisar el presupuesto"
   - **Fecha límite**: 2024-11-24T15:00:00
   - **Prioridad**: high (detectó "importante")

3. **Se crea la tarea automáticamente** con todos los datos estructurados

### Sistema de recomendaciones (suggest-next)

1. **Analiza todas tus tareas**:
   - Estado (pendiente, en progreso, completada)
   - Prioridad (baja, media, alta, urgente)
   - Fecha límite (próximas primero)

2. **Gemini recomienda**:
```json
   {
     "sugerencia": "Deberías completar 'Llamar a Juan' porque vence en 4 horas y tiene alta prioridad",
     "task_id": 42
   }
```

## 🚀 Deploy en Render

### Desde GitHub

1. Push tu código a GitHub
2. Conecta tu repo en [Render](https://render.com)
3. Render detecta automáticamente `render.yaml`
4. Añade `GEMINI_API_KEY` en variables de entorno
5. Deploy automático en cada push a `main`

### Variables de entorno en producción

Render configura automáticamente:
- ✅ `DATABASE_URL` - PostgreSQL connection string
- ✅ `SECRET_KEY` - Generado automáticamente
- ⚠️ `GEMINI_API_KEY` - **Debes añadirlo manualmente**

## 📊 Modelo de datos

### User
```python
- id: int (PK)
- email: string (unique)
- password_hash: string
- nombre: string
- created_at: datetime
- updated_at: datetime
```

### Task
```python
- id: int (PK)
- user_id: int (FK → users.id)
- titulo: string(200)
- descripcion: text
- estado: enum (pending, in_progress, completed, cancelled)
- prioridad: enum (low, medium, high, urgent)
- fecha_limite: datetime (nullable)
- original_input: text (si creada con IA)
- created_by_ai: boolean
- created_at: datetime
- updated_at: datetime
- completed_at: datetime (nullable)
```

## 🔐 Seguridad

- ✅ **Passwords hasheados** con bcrypt (nunca se almacenan en texto plano)
- ✅ **JWT tokens** con expiración de 24 horas
- ✅ **CORS configurado** para dominios permitidos
- ✅ **SQL Injection protection** via SQLAlchemy ORM
- ✅ **Validación de datos** con Pydantic
- ✅ **Rate limiting** en producción (Render)

## 📈 Roadmap

Mejoras futuras planeadas:

- [ ] **Recordatorios automáticos** - Emails/notificaciones antes de deadlines
- [ ] **Colaboración** - Compartir tareas entre usuarios
- [ ] **Categorías/Tags** - Organizar tareas por proyectos
- [ ] **Dashboard de métricas** - Estadísticas de productividad
- [ ] **Frontend web** - Interfaz React/Vue
- [ ] **App móvil** - React Native / Flutter
- [ ] **Webhooks** - Integración con Slack, Discord, etc.
- [ ] **Búsqueda semántica** - Encontrar tareas por contexto con embeddings

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una branch para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 👤 Autor

**Alfredo M. Okenve**

- GitHub: [@alokenveo](https://github.com/alokenveo)
- LinkedIn: [Mi Linkedin](https://linkedin.com/in/alfredo-mituy-okenve-obiang-72180124b)
- Email: fredymituy@gmail.com

## 🙏 Agradecimientos

- [FastAPI](https://fastapi.tiangolo.com/) - Framework increíble
- [Google Gemini](https://ai.google.dev/) - Modelo de IA potente y accesible
<!-- - [Render](https://render.com/) - Hosting simple y eficiente -->

---

⭐️ Si te gustó este proyecto, dale una estrella en GitHub!
```
