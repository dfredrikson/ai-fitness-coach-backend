"""
AI Fitness Coach - Coach & Chat Endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User, Message, CoachPersonality
from app.schemas import (
    CoachPersonalityResponse, CoachPersonalityList,
    ChatMessage, ChatMessageResponse, ChatHistoryResponse, CoachResponse
)
from app.api.deps import get_current_user
from app.services import ai_service
from app.data.coach_personalities import COACH_PERSONALITIES
from app.models.coach_personality import CoachPersonality


router = APIRouter(prefix="/coach", tags=["Entrenador IA"])


@router.get("/personalities", response_model=CoachPersonalityList)
async def list_personalities(db: Session = Depends(get_db)):
    coaches = db.query(CoachPersonality).order_by(CoachPersonality.created_at).all()
    return CoachPersonalityList(items=coaches)


@router.get("/active")
async def get_active_coach(current_user: User = Depends(get_current_user)):
    """Obtener el entrenador activo del usuario."""
    coach = ai_service.get_coach_personality(current_user.active_coach_id)
    
    return {
        "id": coach["id"],
        "name": coach["name"],
        "icon": coach["icon"],
        "description": coach["description"]
    }


@router.put("/active/{coach_id}")
async def set_active_coach(
    coach_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cambiar el entrenador activo."""
    # Verify coach exists
    coach = ai_service.get_coach_personality(coach_id)
    if not coach or coach["id"] != coach_id:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personalidad de entrenador no encontrada"
        )
    
    current_user.active_coach_id = coach_id
    db.commit()
    
    return {
        "message": f"Entrenador cambiado a {coach['name']}",
        "coach": {
            "id": coach["id"],
            "name": coach["name"],
            "icon": coach["icon"]
        }
    }


@router.post("/chat", response_model=CoachResponse)
async def chat_with_coach(
    message: ChatMessage,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Chatear con el entrenador IA."""
    # Save user message
    user_message = Message(
        user_id=current_user.id,
        content=message.content,
        is_from_user=True,
        message_type="chat"
    )
    db.add(user_message)
    db.commit()
    
    # Get chat history
    history = db.query(Message).filter(
        Message.user_id == current_user.id,
        Message.message_type == "chat"
    ).order_by(Message.created_at.desc()).limit(20).all()
    
    history_data = [
        {"content": m.content, "is_from_user": m.is_from_user}
        for m in reversed(history)
    ]
    
    # Get AI response
    coach = ai_service.get_coach_personality(current_user.active_coach_id)
    response_text = await ai_service.chat(
        message.content,
        history_data,
        current_user.active_coach_id
    )
    
    # Save coach response
    coach_message = Message(
        user_id=current_user.id,
        content=response_text,
        is_from_user=False,
        message_type="chat"
    )
    db.add(coach_message)
    db.commit()
    
    return CoachResponse(
        message=response_text,
        coach_name=coach["name"],
        coach_icon=coach["icon"]
    )


@router.get("/chat/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    limit: int = Query(default=50, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener historial de chat con el entrenador."""
    messages = db.query(Message).filter(
        Message.user_id == current_user.id,
        Message.message_type == "chat"
    ).order_by(Message.created_at.desc()).limit(limit).all()
    
    return ChatHistoryResponse(
        messages=[
            ChatMessageResponse(
                id=m.id,
                content=m.content,
                is_from_user=m.is_from_user,
                message_type=m.message_type,
                created_at=m.created_at
            )
            for m in reversed(messages)
        ],
        total=len(messages)
    )
