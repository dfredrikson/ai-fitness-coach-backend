"""
AI Fitness Coach - Authentication Endpoints
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.exceptions import UserAlreadyExistsException, CredentialsException
from app.models import User
from app.models.coach_personality import CoachPersonality
from app.schemas import UserCreate, UserLogin, UserResponse, Token
from app.api.deps import get_current_user
#from app.data.coach_personalities import get_default_coach

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Registrar un nuevo usuario."""
    # Check if email already exists
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise UserAlreadyExistsException()
    
    # Buscar coach default desde la base de datos
    default_coach = db.query(CoachPersonality)\
        .filter(CoachPersonality.is_default == True)\
        .first()

    if not default_coach:
        raise HTTPException(
            status_code=500,
            detail="No hay coach por defecto configurado en el sistema"
        )
    print("PASSWORD RECIBIDO:", user_data.password)
    print("LARGO PASSWORD:", len(user_data.password))

    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        name=user_data.name,
        active_coach_id=default_coach.id
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        language=user.language,
        active_coach_id=user.active_coach_id,
        strava_connected=user.is_strava_connected(),
        created_at=user.created_at
    )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Iniciar sesión y obtener token JWT."""
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise CredentialsException("Email o contraseña incorrectos")
    
    access_token = create_access_token(data={"sub": user.id})
    
    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Obtener información del usuario actual."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        language=current_user.language,
        active_coach_id=current_user.active_coach_id,
        strava_connected=current_user.is_strava_connected(),
        created_at=current_user.created_at
    )
