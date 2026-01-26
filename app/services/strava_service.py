"""
AI Fitness Coach - Strava Service

Handles all Strava API interactions including OAuth and activity sync.
"""
import httpx
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import User, Activity
from app.core.exceptions import StravaAPIException, StravaNotConnectedException

settings = get_settings()


class StravaService:
    """Service for Strava API interactions."""
    
    def __init__(self):
        self.client_id = settings.strava_client_id
        self.client_secret = settings.strava_client_secret
        self.redirect_uri = settings.strava_redirect_uri
        self.auth_url = settings.strava_auth_url
        self.token_url = settings.strava_token_url
        self.api_url = settings.strava_api_url
    
    def get_authorization_url(self, state: str = "") -> str:
        """Generate Strava OAuth authorization URL."""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "read,activity:read_all",
            "state": state
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.auth_url}?{query}"
    
    async def exchange_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "grant_type": "authorization_code"
                }
            )
            
            if response.status_code != 200:
                raise StravaAPIException(f"Error al obtener token: {response.text}")
            
            return response.json()
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh expired access token."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token"
                }
            )
            
            if response.status_code != 200:
                raise StravaAPIException("Error al refrescar token de Strava")
            
            return response.json()
    
    async def ensure_valid_token(self, user: User, db: Session) -> str:
        """Ensure user has a valid access token, refresh if needed."""
        if not user.strava_access_token:
            raise StravaNotConnectedException()
        
        # Check if token is expired (with 5 minute buffer)
        if user.strava_token_expires and user.strava_token_expires <= datetime.utcnow() + timedelta(minutes=5):
            token_data = await self.refresh_token(user.strava_refresh_token)
            
            user.strava_access_token = token_data["access_token"]
            user.strava_refresh_token = token_data["refresh_token"]
            user.strava_token_expires = datetime.fromtimestamp(token_data["expires_at"])
            db.commit()
        
        return user.strava_access_token
    
    async def get_athlete(self, access_token: str) -> Dict[str, Any]:
        """Get authenticated athlete info."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/athlete",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code != 200:
                raise StravaAPIException("Error al obtener información del atleta")
            
            return response.json()
    
    async def get_activities(
        self, 
        access_token: str, 
        page: int = 1, 
        per_page: int = 30,
        after: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get list of athlete activities."""
        params = {"page": page, "per_page": per_page}
        if after:
            params["after"] = after
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/athlete/activities",
                headers={"Authorization": f"Bearer {access_token}"},
                params=params
            )
            
            if response.status_code != 200:
                raise StravaAPIException("Error al obtener actividades")
            
            return response.json()
    
    async def get_activity_detail(self, access_token: str, activity_id: int) -> Dict[str, Any]:
        """Get detailed activity information."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/activities/{activity_id}",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code != 200:
                raise StravaAPIException(f"Error al obtener actividad {activity_id}")
            
            return response.json()
    
    def parse_activity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Strava activity data into our model format."""
        # Calculate pace (min/km) for runs
        avg_pace = None
        max_pace = None
        
        if data.get("type") == "Run" and data.get("distance", 0) > 0:
            distance_km = data["distance"] / 1000
            duration_min = data.get("moving_time", 0) / 60
            avg_pace = duration_min / distance_km if distance_km > 0 else None
        
        return {
            "strava_id": data["id"],
            "type": data.get("type", "Unknown"),
            "name": data.get("name", "Sin nombre"),
            "start_date": datetime.fromisoformat(data["start_date"].replace("Z", "+00:00")),
            "distance_meters": data.get("distance", 0),
            "duration_seconds": data.get("moving_time", 0),
            "avg_pace": avg_pace,
            "avg_heartrate": data.get("average_heartrate"),
            "max_heartrate": data.get("max_heartrate"),
            "elevation_gain": data.get("total_elevation_gain", 0),
            "calories": data.get("calories"),
            "raw_data": data
        }
    
    async def sync_activities(
        self, 
        user: User, 
        db: Session, 
        limit: int = 30
    ) -> List[Activity]:
        """Sync activities from Strava to database."""
        access_token = await self.ensure_valid_token(user, db)
        
        # Get activities from Strava
        strava_activities = await self.get_activities(access_token, per_page=limit)
        
        synced = []
        for activity_data in strava_activities:
            # Check if already exists
            existing = db.query(Activity).filter(
                Activity.strava_id == activity_data["id"]
            ).first()
            
            if existing:
                continue
            
            # Parse and create new activity
            parsed = self.parse_activity(activity_data)
            activity = Activity(user_id=user.id, **parsed)
            db.add(activity)
            synced.append(activity)
        
        if synced:
            db.commit()
            for a in synced:
                db.refresh(a)
        
        return synced


# Singleton instance
strava_service = StravaService()
