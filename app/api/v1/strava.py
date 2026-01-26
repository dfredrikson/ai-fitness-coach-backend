"""
AI Fitness Coach - Strava Integration Endpoints
"""
from datetime import datetime
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User
from app.schemas import ActivityListResponse
from app.api.deps import get_current_user
from app.services import strava_service

router = APIRouter(prefix="/strava", tags=["Strava"])


@router.get("/connect")
async def connect_strava(current_user: User = Depends(get_current_user)):
    """Obtener URL de autorización de Strava."""
    auth_url = strava_service.get_authorization_url(state=current_user.id)
    return {"authorization_url": auth_url}


@router.get("/callback")
async def strava_callback(
    code: str = Query(...),
    state: str = Query(default=""),
    db: Session = Depends(get_db)
):
    """Callback de OAuth de Strava."""
    # Exchange code for token
    token_data = await strava_service.exchange_token(code)
    
    # Get user from state (user_id)
    user = db.query(User).filter(User.id == state).first()
    
    if not user:
        return RedirectResponse(url="/login?error=user_not_found")
    
    # Save tokens
    user.strava_athlete_id = str(token_data["athlete"]["id"])
    user.strava_access_token = token_data["access_token"]
    user.strava_refresh_token = token_data["refresh_token"]
    user.strava_token_expires = datetime.fromtimestamp(token_data["expires_at"])
    
    db.commit()
    
    # Redirect to frontend success page
    return RedirectResponse(url="http://localhost:5173/dashboard?strava=connected")


@router.post("/disconnect")
async def disconnect_strava(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Desconectar cuenta de Strava."""
    current_user.strava_athlete_id = None
    current_user.strava_access_token = None
    current_user.strava_refresh_token = None
    current_user.strava_token_expires = None
    
    db.commit()
    
    return {"message": "Strava desconectado correctamente"}


@router.get("/status")
async def strava_status(current_user: User = Depends(get_current_user)):
    """Verificar estado de conexión con Strava."""
    return {
        "connected": current_user.is_strava_connected(),
        "athlete_id": current_user.strava_athlete_id
    }


@router.post("/sync")
async def sync_activities(
    limit: int = Query(default=30, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sincronizar actividades desde Strava."""
    synced = await strava_service.sync_activities(current_user, db, limit=limit)
    
    return {
        "message": f"Se sincronizaron {len(synced)} actividades nuevas",
        "synced_count": len(synced),
        "activities": [
            {
                "id": a.id,
                "name": a.name,
                "type": a.type,
                "distance_km": a.distance_km
            }
            for a in synced
        ]
    }
