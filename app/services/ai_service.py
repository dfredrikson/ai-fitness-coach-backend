"""
AI Fitness Coach - AI Service

Handles LLM interactions for activity analysis and chat.
"""
from typing import Optional, List, Dict, Any
# from openai import OpenAI

from app.config import get_settings
from app.core.exceptions import AIServiceException
from app.data.coach_personalities import COACH_PERSONALITIES, get_coach_by_id, get_default_coach

settings = get_settings()


class AIService:
    """Service for AI/LLM interactions."""
    
    def __init__(self):
        self.client = None
        self.model = "mock"

    #def __init__(self):
        #self.client = OpenAI(api_key=settings.openai_api_key)
        #self.model = settings.openai_model
    
    def get_coach_personality(self, coach_id: Optional[str] = None) -> Dict[str, Any]:
        """Get coach personality by ID or return default."""
        if coach_id:
            coach = get_coach_by_id(coach_id)
            if coach:
                return coach
        return get_default_coach()
    
    def _build_activity_context(self, activity: Dict[str, Any]) -> str:
        """Build context string from activity data."""
        context = f"""
Datos del entrenamiento:
- Tipo: {activity.get('type', 'Desconocido')}
- Nombre: {activity.get('name', 'Sin nombre')}
- Fecha: {activity.get('start_date', 'No disponible')}
- Distancia: {activity.get('distance_km', 0):.2f} km
- Duración: {activity.get('duration_minutes', 0):.0f} minutos
- Ritmo promedio: {activity.get('avg_pace', 'N/A')} min/km
"""
        
        if activity.get('avg_heartrate'):
            context += f"- Frecuencia cardíaca promedio: {activity['avg_heartrate']} bpm\n"
        if activity.get('max_heartrate'):
            context += f"- Frecuencia cardíaca máxima: {activity['max_heartrate']} bpm\n"
        if activity.get('elevation_gain'):
            context += f"- Desnivel acumulado: {activity['elevation_gain']:.0f} m\n"
        if activity.get('calories'):
            context += f"- Calorías: {activity['calories']}\n"
        
        return context
    
    async def analyze_activity(
        self, 
        activity: Dict[str, Any],
        coach_id: Optional[str] = None
        ) -> Dict[str, str]:
        """Analyze an activity and generate feedback (MOCK MODE)."""

        # Simulación de análisis para pruebas (sin usar IA real)
        distance = activity.get("distance_km", 0)
        duration = activity.get("duration_minutes", 0)
        pace = activity.get("avg_pace", "N/A")

        technical = (
            f"Completaste una sesión de {distance:.2f} km en {duration:.0f} minutos. "
            f"El ritmo promedio fue de {pace} min/km. Buen control general del entrenamiento."
        )

        corrections = (
            "Podrías mejorar manteniendo un ritmo más estable en la segunda mitad del entrenamiento "
            "y agregando una sesión semanal de técnica de carrera para optimizar eficiencia."
        )

        motivation = (
            "¡Muy buen trabajo! Este tipo de constancia es la que genera resultados reales. "
            "Seguí así, estás construyendo una base excelente."
        )

        return {
            "technical_analysis": technical,
            "corrections": corrections,
            "motivation": motivation,
            "full_response": technical + "\n\n" + corrections + "\n\n" + motivation
        }

    
    async def chat(
        self,
        message: str,
        history: List[Dict[str, str]],
        coach_id: Optional[str] = None,
        context: Optional[str] = None
    ) -> str:
        """Chat with the AI coach."""
        coach = self.get_coach_personality(coach_id)
        
        system_prompt = coach["system_prompt"]
        if context:
            system_prompt += f"\n\nContexto adicional del usuario:\n{context}"
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add history
        for msg in history[-10:]:  # Last 10 messages for context
            role = "user" if msg.get("is_from_user") else "assistant"
            messages.append({"role": role, "content": msg["content"]})
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        try:
            #response = self.client.chat.completions.create(
            #    model=self.model,
            #    messages=messages,
            #    temperature=coach["style_params"].get("temperature", 0.7),
            #    max_tokens=800
            #)
            
            #return response.choices[0].message.content
            return f"Hola 👋 Soy tu entrenador ({coach['name']}). Dijiste: {message}"

            
        except Exception as e:
            raise AIServiceException(f"Error en chat: {str(e)}")
    
    async def generate_routine_reminder(
        self,
        missed_activity: Dict[str, Any],
        coach_id: Optional[str] = None
    ) -> str:
        """Generate a reminder message for missed routine activity."""
        coach = self.get_coach_personality(coach_id)
        
        prompt = f"""El atleta no ha completado su entrenamiento programado de hoy:
- Día: {missed_activity.get('day_name', 'Hoy')}
- Actividad esperada: {missed_activity.get('activity_type', 'Entrenamiento')}
- Distancia objetivo: {missed_activity.get('target_distance', 'No especificada')} km
- Duración objetivo: {missed_activity.get('target_duration', 'No especificada')} minutos

Genera un mensaje breve (máximo 3 oraciones) recordándole su compromiso y motivándolo a completar el entrenamiento."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": coach["system_prompt"]},
                    {"role": "user", "content": prompt}
                ],
                temperature=coach["style_params"].get("temperature", 0.7),
                max_tokens=200
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise AIServiceException(f"Error generando recordatorio: {str(e)}")


# Singleton instance
ai_service = AIService()
