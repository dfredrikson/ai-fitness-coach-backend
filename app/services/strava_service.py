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
        access_token=None,
        token=None,
        page: int = 1,
        per_page: int = 30,
        after: Optional[int] = None
    ):
        access_token = access_token or token

        if not access_token:
            raise Exception("Missing Strava access token")

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
                print(f"❌ Strava API Warning: {response.status_code} - {response.text}")
                raise StravaAPIException(f"Error al obtener actividades: {response.status_code}")

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

    async def sync_activities(self, user, db, limit=30):
        try:
            if not user.is_strava_connected():
                return []

            # Ensure token is valid (refresh if needed)
            access_token = await self.ensure_valid_token(user, db)

            # 1. Fetch recent activities from Strava
            strava_activities = await self.get_activities(
                access_token,
                page=1,
                per_page=limit
            ) or []

            if not strava_activities:
                return []

            # 2. Determine time window for "Mirroring"
            strava_activities.sort(key=lambda x: x.get("start_date", ""), reverse=True)
            
            oldest_activity = strava_activities[-1]
            min_date_str = oldest_activity.get("start_date", "").replace("Z", "+00:00")
            if not min_date_str:
                return [] # Skip if invalid data
                
            try:
                min_date = datetime.fromisoformat(min_date_str)
            except ValueError:
                print("⚠️ Error parsing min_date:", min_date_str)
                return []

            # 3. Query DB only for activities in this window
            existing_in_window = db.query(Activity).filter(
                Activity.user_id == user.id,
                Activity.start_date >= min_date
            ).all()
            
            existing_map = {str(a.strava_id): a for a in existing_in_window if a.strava_id}
            strava_map = {str(a["id"]): a for a in strava_activities if a.get("id")}
            
            # 4. Calculate diffs
            potential_new_ids = set(strava_map.keys()) - set(existing_map.keys())
            deleted_ids = set(existing_map.keys()) - set(strava_map.keys())

            new_activities = []

            # Check Global Existence for New IDs (Avoid IntegrityError)
            if potential_new_ids:
                global_existing = db.query(Activity.strava_id).filter(
                    Activity.strava_id.in_([int(sid) for sid in potential_new_ids])
                ).all()
                global_existing_ids = {str(r[0]) for r in global_existing}
                real_new_ids = potential_new_ids - global_existing_ids
            else:
                real_new_ids = set()

            # Insert new activities
            for sid in real_new_ids:
                act = strava_map[sid]
                try:
                    start_date_str = act.get("start_date", "")
                    if start_date_str:
                        if start_date_str.endswith("Z"):
                            start_date_str = start_date_str.replace("Z", "+00:00")
                        start_date = datetime.fromisoformat(start_date_str)
                    else:
                        start_date = datetime.utcnow()

                    activity = Activity(
                        user_id=user.id,
                        strava_id=int(sid),
                        name=act.get("name", "Actividad"),
                        type=act.get("type", "Workout"),
                        start_date=start_date,
                        distance_meters=act.get("distance", 0),
                        duration_seconds=act.get("moving_time", 0),
                        elevation_gain=act.get("total_elevation_gain", 0),
                        calories=act.get("calories"),
                        avg_heartrate=act.get("average_heartrate"),
                        max_heartrate=act.get("max_heartrate"),
                        raw_data=act,
                        analyzed=False
                    )

                    db.add(activity)
                    new_activities.append(activity)

                except Exception as e:
                    print(f"❌ Error creating activity object {sid}: {e}")

            # Delete removed activities (Mirroring)
            if deleted_ids:
                print(f"🗑️ Deleting {len(deleted_ids)} activities removed from Strava in this window.")
                db.query(Activity).filter(
                    Activity.user_id == user.id,
                    Activity.strava_id.in_([int(x) for x in deleted_ids])
                ).delete(synchronize_session=False)

            db.commit()

            return new_activities

        except Exception as e:
            print(f"🔥 CRITICAL ERROR in sync_activities: {e}")
            import traceback
            traceback.print_exc()
            db.rollback()
            return [] # Return empty list on crash so frontend receives 200 OK (empty) instead of 502


    async def refresh_access_token(self, user, db):
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.post(
                    "https://www.strava.com/oauth/token",
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "grant_type": "refresh_token",
                        "refresh_token": user.strava_refresh_token
                    }
                )

            if response.status_code != 200:
                print("❌ Refresh token inválido:", response.text)
                return None

            token_data = response.json()

            user.strava_access_token = token_data["access_token"]
            user.strava_refresh_token = token_data["refresh_token"]
            user.strava_token_expires = datetime.fromtimestamp(token_data["expires_at"])

            db.commit()

            return user.strava_access_token

        except Exception as e:
            print("❌ Error refrescando token:", e)
            return None





# Singleton instance
strava_service = StravaService()
