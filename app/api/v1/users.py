"""
AI Fitness Coach - Users Endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User
from app.schemas import UserUpdate, UserResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/users", tags=["Usuarios"])


@router.put("/me", response_model=UserResponse)
async def update_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar información del usuario actual."""
    if user_data.name is not None:
        current_user.name = user_data.name
    
    if user_data.language is not None:
        current_user.language = user_data.language
    
    if user_data.active_coach_id is not None:
        current_user.active_coach_id = user_data.active_coach_id
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        language=current_user.language,
        active_coach_id=current_user.active_coach_id,
        strava_connected=current_user.is_strava_connected(),
        created_at=current_user.created_at
    )


@router.delete("/me")
async def delete_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar cuenta del usuario actual."""
    db.delete(current_user)
    db.commit()
    
    return {"message": "Cuenta eliminada correctamente"}
