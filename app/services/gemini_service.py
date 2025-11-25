from google import genai
from app.config import settings
from typing import Optional
from datetime import datetime, timedelta
import json
from google.genai import types

# ==========================================
# CLIENTE GEMINI
# ==========================================

client = genai.Client(api_key=settings.gemini_api_key)

# ==========================================
# PROMPTS DEL SISTEMA
# ==========================================

TASK_EXTRACTION_PROMPT = """Eres un asistente de productividad experto. Tu trabajo es extraer información estructurada de las solicitudes del usuario para crear tareas.

Analiza el siguiente texto y extrae:
- titulo: Un título conciso de la tarea (máximo 50 caracteres)
- descripcion: Descripción detallada (opcional, puede ser null)
- fecha_limite: Fecha y hora en formato ISO 8601 (YYYY-MM-DDTHH:MM:SS). Si no se menciona fecha específica, usa null.
- prioridad: "low", "medium", "high" o "urgent" según el contexto

Reglas para fecha_limite:
- Hoy es {fecha_actual}
- "mañana" = {fecha_manana}
- "pasado mañana" = {fecha_pasado_manana}
- "próximo lunes/martes/etc" = calcular según el día actual
- "en 3 días" = sumar días a la fecha actual
- Si no hay fecha mencionada, usa null

Reglas para prioridad:
- "urgente", "ya", "inmediatamente" → urgent
- "importante" → high
- Por defecto → medium
- "cuando pueda", "no corre prisa" → low

Responde SOLO con un objeto JSON válido (sin markdown, sin explicaciones):
{{
  "titulo": "...",
  "descripcion": "..." o null,
  "fecha_limite": "YYYY-MM-DDTHH:MM:SS" o null,
  "prioridad": "low|medium|high|urgent"
}}"""


SUGGEST_NEXT_PROMPT = """Eres un asistente de productividad. Analiza las tareas del usuario y sugiere cuál debería hacer ahora.

Tareas del usuario:
{tareas_json}

Fecha y hora actual: {fecha_actual}

Considera:
1. Tareas con fecha_limite próxima (urgentes)
2. Tareas con prioridad alta
3. Tareas pendientes vs en progreso

Responde SOLO con un objeto JSON:
{{
  "sugerencia": "Texto amigable explicando qué hacer y por qué",
  "task_id": ID de la tarea sugerida (int) o null si no hay tareas
}}"""


# ==========================================
# FUNCIÓN: EXTRAER DATOS DE TAREA
# ==========================================


def extract_task_data(user_input: str) -> dict:
    """
    Usa Gemini para extraer datos estructurados desde lenguaje natural.

    Ejemplo:
        extract_task_data("Llamar al dentista mañana 10am")
        → {
            "titulo": "Llamar al dentista",
            "descripcion": null,
            "fecha_limite": "2024-11-24T10:00:00",
            "prioridad": "medium"
          }

    Args:
        user_input: Texto del usuario en lenguaje natural

    Returns:
        Dict con titulo, descripcion, fecha_limite, prioridad

    Raises:
        ValueError: Si Gemini no puede procesar el texto o devuelve JSON inválido
    """
    
    hoy = datetime.now()
    manana = hoy + timedelta(days=1)
    pasado_manana = hoy + timedelta(days=2)

    prompt = TASK_EXTRACTION_PROMPT.format(
        fecha_actual=hoy.strftime("%Y-%m-%d %H:%M:%S"),
        fecha_manana=manana.strftime("%Y-%m-%d"),
        fecha_pasado_manana=pasado_manana.strftime("%Y-%m-%d"),
    )

    schema = {
        "type": "OBJECT",
        "properties": {
            "titulo": {"type": "STRING"},
            "descripcion": {"type": "STRING", "nullable": True},
            "fecha_limite": {"type": "STRING", "nullable": True},
            "prioridad": {"type": "STRING"},
        },
        "required": ["titulo", "prioridad"],
    }

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt + "\n\nTexto del usuario: " + user_input,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": schema
            },
        )

        response_text = response.text.strip()

        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]

        data = json.loads(response_text.strip())

        return {
            "titulo": data.get("titulo"),
            "descripcion": data.get("descripcion"),
            "fecha_limite": data.get("fecha_limite"),
            "prioridad": data.get("prioridad"),
        }

    except json.JSONDecodeError as e:
        raise ValueError(f"Gemini devolvió JSON inválido: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error al procesar con Gemini: {str(e)}")


def suggest_next_task(tasks: list) -> dict:
    """
    Usa Gemini para sugerir qué tarea hacer ahora.
    
    Args:
        tasks: Lista de tareas del usuario (dicts con id, titulo, estado, etc.)
        
    Returns:
        {
          "sugerencia": "Deberías completar X porque...",
          "task_id": 123 o null
        }
    """
    
    if not tasks:
        return {
            "sugerencia": "No tienes tareas pendientes. ¡Buen trabajo! ¿Quieres crear una nueva?",
            "task_id": None
        }
    
    active_tasks = [
        t for t in tasks 
        if t.get("estado") in ["pending", "in_progress"]
    ]
    
    if not active_tasks:
        return {
            "sugerencia": "¡Todas tus tareas están completadas! 🎉",
            "task_id": None
        }
    
    tareas_simplificadas = [
        {
            "id": t.get("id"),
            "titulo": t.get("titulo"),
            "prioridad": t.get("prioridad"),
            "fecha_limite": t.get("fecha_limite").isoformat() if t.get("fecha_limite") else None,
            "estado": t.get("estado")
        }
        for t in active_tasks
    ]
    
    prompt = SUGGEST_NEXT_PROMPT.format(
        tareas_json=json.dumps(tareas_simplificadas, indent=2, ensure_ascii=False),
        fecha_actual=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    
    schema = {
        "type": "OBJECT",
        "properties": {
            "sugerencia": {"type": "STRING"},
            "task_id": {"type": "INTEGER", "nullable": True}
        },
        "required": ["sugerencia"]
    }
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt + "\n\nPregunta del usuario: ¿Qué tarea debería hacer ahora?",
            config={
                "response_mime_type": "application/json",
                "response_json_schema": schema
            }
        )
        
        response_text = response.text.strip()
        
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        data = json.loads(response_text.strip())
        
        return {
            "sugerencia": data.get("sugerencia", "No pude generar una sugerencia"),
            "task_id": data.get("task_id")
        }
        
    except Exception as e:
        urgent_task = min(
            active_tasks,
            key=lambda t: (
                t.get("fecha_limite") or datetime.max,
                {"urgent": 0, "high": 1, "medium": 2, "low": 3}.get(t.get("prioridad"), 2)
            )
        )
        
        return {
            "sugerencia": f"Te sugiero completar: '{urgent_task.get('titulo')}' (prioridad {urgent_task.get('prioridad')})",
            "task_id": urgent_task.get("id")
        }