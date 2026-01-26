"""
AI Fitness Coach - Activities Endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User, Activity, AIAnalysis
from app.schemas import (
    ActivityResponse, ActivityListResponse, 
    ActivityWithAnalysis, AIAnalysisResponse
)
from app.api.deps import get_current_user
from app.services import analysis_service

router = APIRouter(prefix="/activities", tags=["Actividades"])


@router.get("", response_model=ActivityListResponse)
async def list_activities(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, le=100),
    activity_type: Optional[str] = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar actividades del usuario."""
    query = db.query(Activity).filter(Activity.user_id == current_user.id)
    
    if activity_type:
        query = query.filter(Activity.type == activity_type)
    
    total = query.count()
    activities = query.order_by(Activity.start_date.desc())\
        .offset((page - 1) * page_size)\
        .limit(page_size)\
        .all()
    
    return ActivityListResponse(
        items=[
            ActivityResponse(
                id=a.id,
                strava_id=a.strava_id,
                type=a.type,
                name=a.name,
                start_date=a.start_date,
                distance_meters=a.distance_meters,
                duration_seconds=a.duration_seconds,
                avg_pace=a.avg_pace,
                max_pace=a.max_pace,
                avg_heartrate=a.avg_heartrate,
                max_heartrate=a.max_heartrate,
                elevation_gain=a.elevation_gain,
                calories=a.calories,
                analyzed=a.analyzed,
                synced_at=a.synced_at,
                distance_km=a.distance_km,
                duration_minutes=a.duration_minutes
            )
            for a in activities
        ],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{activity_id}", response_model=ActivityWithAnalysis)
async def get_activity(
    activity_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener detalle de una actividad con su análisis."""
    activity = db.query(Activity).filter(
        Activity.id == activity_id,
        Activity.user_id == current_user.id
    ).first()
    
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Actividad no encontrada"
        )
    
    analyses = db.query(AIAnalysis).filter(
        AIAnalysis.activity_id == activity_id
    ).order_by(AIAnalysis.created_at.desc()).all()
    
    return ActivityWithAnalysis(
        id=activity.id,
        strava_id=activity.strava_id,
        type=activity.type,
        name=activity.name,
        start_date=activity.start_date,
        distance_meters=activity.distance_meters,
        duration_seconds=activity.duration_seconds,
        avg_pace=activity.avg_pace,
        max_pace=activity.max_pace,
        avg_heartrate=activity.avg_heartrate,
        max_heartrate=activity.max_heartrate,
        elevation_gain=activity.elevation_gain,
        calories=activity.calories,
        analyzed=activity.analyzed,
        synced_at=activity.synced_at,
        distance_km=activity.distance_km,
        duration_minutes=activity.duration_minutes,
        analyses=[
            AIAnalysisResponse(
                id=a.id,
                activity_id=a.activity_id,
                coach_personality_id=a.coach_personality_id,
                technical_analysis=a.technical_analysis,
                corrections=a.corrections,
                motivation=a.motivation,
                metrics_summary=a.metrics_summary,
                created_at=a.created_at
            )
            for a in analyses
        ]
    )


@router.post("/{activity_id}/analyze", response_model=AIAnalysisResponse)
async def analyze_activity(
    activity_id: str,
    force: bool = Query(default=False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analizar una actividad con el coach IA."""
    activity = db.query(Activity).filter(
        Activity.id == activity_id,
        Activity.user_id == current_user.id
    ).first()
    
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Actividad no encontrada"
        )
    
    analysis = await analysis_service.analyze_activity(
        activity, current_user, db, force=force
    )
    
    return AIAnalysisResponse(
        id=analysis.id,
        activity_id=analysis.activity_id,
        coach_personality_id=analysis.coach_personality_id,
        technical_analysis=analysis.technical_analysis,
        corrections=analysis.corrections,
        motivation=analysis.motivation,
        metrics_summary=analysis.metrics_summary,
        created_at=analysis.created_at
    )
