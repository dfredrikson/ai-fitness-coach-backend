"""
AI Fitness Coach - API Dependencies
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token
from app.core.exceptions import CredentialsException
from app.models import User

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token."""
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise CredentialsException()
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise CredentialsException()
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise CredentialsException("Usuario no encontrado")
    
    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, otherwise return None."""
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None
