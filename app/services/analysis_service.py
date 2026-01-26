"""
AI Fitness Coach - Analysis Service

Handles activity analysis with AI and storage.
"""
from typing import Optional
from sqlalchemy.orm import Session

from app.models import Activity, AIAnalysis, User
from app.services.ai_service import ai_service


class AnalysisService:
    """Service for activity analysis."""
    
    async def analyze_activity(
        self,
        activity: Activity,
        user: User,
        db: Session,
        force: bool = False
    ) -> AIAnalysis:
        """Analyze an activity and store the analysis."""
        
        # Check if already analyzed (unless forced)
        if activity.analyzed and not force:
            existing = db.query(AIAnalysis).filter(
                AIAnalysis.activity_id == activity.id
            ).order_by(AIAnalysis.created_at.desc()).first()
            
            if existing:
                return existing
        
        # Prepare activity data for AI
        activity_data = {
            "type": activity.type,
            "name": activity.name,
            "start_date": activity.start_date.isoformat() if activity.start_date else None,
            "distance_km": activity.distance_km,
            "duration_minutes": activity.duration_minutes,
            "avg_pace": f"{activity.avg_pace:.2f}" if activity.avg_pace else None,
            "avg_heartrate": activity.avg_heartrate,
            "max_heartrate": activity.max_heartrate,
            "elevation_gain": activity.elevation_gain,
            "calories": activity.calories
        }
        
        # Get coach ID from user preferences
        coach_id = user.active_coach_id
        
        # Analyze with AI
        analysis_result = await ai_service.analyze_activity(activity_data, coach_id)
        
        # Create analysis record
        analysis = AIAnalysis(
            activity_id=activity.id,
            coach_personality_id=coach_id or "coach-motivador",
            technical_analysis=analysis_result["technical_analysis"],
            corrections=analysis_result["corrections"],
            motivation=analysis_result["motivation"],
            metrics_summary={
                "distance_km": activity.distance_km,
                "duration_minutes": activity.duration_minutes,
                "avg_pace": activity.avg_pace,
                "avg_heartrate": activity.avg_heartrate
            }
        )
        
        db.add(analysis)
        activity.analyzed = True
        db.commit()
        db.refresh(analysis)
        
        return analysis
    
    async def analyze_new_activities(
        self,
        user: User,
        db: Session,
        limit: int = 5
    ) -> list:
        """Analyze all unanalyzed activities for a user."""
        unanalyzed = db.query(Activity).filter(
            Activity.user_id == user.id,
            Activity.analyzed == False
        ).order_by(Activity.start_date.desc()).limit(limit).all()
        
        analyses = []
        for activity in unanalyzed:
            analysis = await self.analyze_activity(activity, user, db)
            analyses.append(analysis)
        
        return analyses


# Singleton instance
analysis_service = AnalysisService()
