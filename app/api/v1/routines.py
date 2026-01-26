"""
AI Fitness Coach - Routines Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User, Routine, RoutineDay
from app.schemas import (
    RoutineCreate, RoutineUpdate, RoutineResponse, 
    RoutineListResponse, RoutineDayResponse, RoutineComplianceResponse
)
from app.api.deps import get_current_user
from app.services import routine_service

router = APIRouter(prefix="/routines", tags=["Rutinas"])


@router.get("", response_model=RoutineListResponse)
async def list_routines(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar rutinas del usuario."""
    routines = db.query(Routine).filter(
        Routine.user_id == current_user.id
    ).order_by(Routine.created_at.desc()).all()
    
    return RoutineListResponse(
        items=[
            RoutineResponse(
                id=r.id,
                name=r.name,
                is_active=r.is_active,
                days=[
                    RoutineDayResponse(
                        id=d.id,
                        day_of_week=d.day_of_week,
                        activity_type=d.activity_type,
                        target_distance=d.target_distance,
                        target_duration=d.target_duration,
                        notes=d.notes,
                        day_name=d.day_name
                    )
                    for d in r.days
                ],
                created_at=r.created_at,
                updated_at=r.updated_at
            )
            for r in routines
        ]
    )


@router.post("", response_model=RoutineResponse, status_code=status.HTTP_201_CREATED)
async def create_routine(
    routine_data: RoutineCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear una nueva rutina."""
    routine = Routine(
        user_id=current_user.id,
        name=routine_data.name
    )
    
    db.add(routine)
    db.flush()
    
    # Add days
    for day_data in routine_data.days:
        day = RoutineDay(
            routine_id=routine.id,
            day_of_week=day_data.day_of_week,
            activity_type=day_data.activity_type,
            target_distance=day_data.target_distance,
            target_duration=day_data.target_duration,
            notes=day_data.notes
        )
        db.add(day)
    
    db.commit()
    db.refresh(routine)
    
    return RoutineResponse(
        id=routine.id,
        name=routine.name,
        is_active=routine.is_active,
        days=[
            RoutineDayResponse(
                id=d.id,
                day_of_week=d.day_of_week,
                activity_type=d.activity_type,
                target_distance=d.target_distance,
                target_duration=d.target_duration,
                notes=d.notes,
                day_name=d.day_name
            )
            for d in routine.days
        ],
        created_at=routine.created_at,
        updated_at=routine.updated_at
    )


@router.get("/{routine_id}", response_model=RoutineResponse)
async def get_routine(
    routine_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener detalle de una rutina."""
    routine = db.query(Routine).filter(
        Routine.id == routine_id,
        Routine.user_id == current_user.id
    ).first()
    
    if not routine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rutina no encontrada"
        )
    
    return RoutineResponse(
        id=routine.id,
        name=routine.name,
        is_active=routine.is_active,
        days=[
            RoutineDayResponse(
                id=d.id,
                day_of_week=d.day_of_week,
                activity_type=d.activity_type,
                target_distance=d.target_distance,
                target_duration=d.target_duration,
                notes=d.notes,
                day_name=d.day_name
            )
            for d in routine.days
        ],
        created_at=routine.created_at,
        updated_at=routine.updated_at
    )


@router.put("/{routine_id}", response_model=RoutineResponse)
async def update_routine(
    routine_id: str,
    routine_data: RoutineUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar una rutina."""
    routine = db.query(Routine).filter(
        Routine.id == routine_id,
        Routine.user_id == current_user.id
    ).first()
    
    if not routine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rutina no encontrada"
        )
    
    if routine_data.name is not None:
        routine.name = routine_data.name
    
    if routine_data.is_active is not None:
        routine.is_active = routine_data.is_active
    
    if routine_data.days is not None:
        # Delete existing days
        db.query(RoutineDay).filter(RoutineDay.routine_id == routine_id).delete()
        
        # Add new days
        for day_data in routine_data.days:
            day = RoutineDay(
                routine_id=routine.id,
                day_of_week=day_data.day_of_week,
                activity_type=day_data.activity_type,
                target_distance=day_data.target_distance,
                target_duration=day_data.target_duration,
                notes=day_data.notes
            )
            db.add(day)
    
    db.commit()
    db.refresh(routine)
    
    return RoutineResponse(
        id=routine.id,
        name=routine.name,
        is_active=routine.is_active,
        days=[
            RoutineDayResponse(
                id=d.id,
                day_of_week=d.day_of_week,
                activity_type=d.activity_type,
                target_distance=d.target_distance,
                target_duration=d.target_duration,
                notes=d.notes,
                day_name=d.day_name
            )
            for d in routine.days
        ],
        created_at=routine.created_at,
        updated_at=routine.updated_at
    )


@router.delete("/{routine_id}")
async def delete_routine(
    routine_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar una rutina."""
    routine = db.query(Routine).filter(
        Routine.id == routine_id,
        Routine.user_id == current_user.id
    ).first()
    
    if not routine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rutina no encontrada"
        )
    
    db.delete(routine)
    db.commit()
    
    return {"message": "Rutina eliminada correctamente"}


@router.get("/{routine_id}/compliance")
async def get_routine_compliance(
    routine_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener reporte de cumplimiento de la rutina esta semana."""
    routine = db.query(Routine).filter(
        Routine.id == routine_id,
        Routine.user_id == current_user.id
    ).first()
    
    if not routine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rutina no encontrada"
        )
    
    compliance = routine_service.get_weekly_compliance(routine, db)
    
    return compliance
