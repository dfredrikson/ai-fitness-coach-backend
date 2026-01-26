"""
AI Fitness Coach - Custom Exceptions
"""
from fastapi import HTTPException, status


class CredentialsException(HTTPException):
    """Exception for invalid credentials."""
    def __init__(self, detail: str = "No se pudieron validar las credenciales"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class UserNotFoundException(HTTPException):
    """Exception for user not found."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )


class UserAlreadyExistsException(HTTPException):
    """Exception for duplicate user."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )


class StravaNotConnectedException(HTTPException):
    """Exception when Strava is not connected."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cuenta de Strava no conectada"
        )


class StravaAPIException(HTTPException):
    """Exception for Strava API errors."""
    def __init__(self, detail: str = "Error al comunicarse con Strava"):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail
        )


class AIServiceException(HTTPException):
    """Exception for AI service errors."""
    def __init__(self, detail: str = "Error en el servicio de IA"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail
        )
