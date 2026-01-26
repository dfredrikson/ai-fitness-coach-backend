"""
AI Fitness Coach - Routine Service

Handles routine management and compliance checking.
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models import Routine, RoutineDay, Activity, User
from app.services.ai_service import ai_service


class RoutineService:
    """Service for routine management."""
    
    def get_week_boundaries(self, date: Optional[datetime] = None) -> tuple:
        """Get start and end of the week containing the given date."""
        if date is None:
            date = datetime.utcnow()
        
        # Monday = 0, Sunday = 6
        start = date - timedelta(days=date.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=7)
        
        return start, end
    
    def check_day_compliance(
        self,
        routine_day: RoutineDay,
        activities: List[Activity]
    ) -> Dict[str, Any]:
        """Check if activities match routine day requirements."""
        # Filter activities by type
        matching = [
            a for a in activities 
            if a.type and a.type.lower() == routine_day.activity_type.lower()
        ]
        
        if not matching:
            return {
                "completed": False,
                "actual_activity": None,
                "reason": "No se encontró actividad del tipo esperado"
            }
        
        # Get the best matching activity (longest distance/duration)
        best = max(matching, key=lambda a: a.distance_meters or 0)
        
        completed = True
        reasons = []
        
        # Check distance target
        if routine_day.target_distance:
            if best.distance_km < routine_day.target_distance * 0.9:  # 90% tolerance
                completed = False
                reasons.append(f"Distancia: {best.distance_km:.2f} km < {routine_day.target_distance} km objetivo")
        
        # Check duration target
        if routine_day.target_duration:
            if best.duration_minutes < routine_day.target_duration * 0.9:  # 90% tolerance
                completed = False
                reasons.append(f"Duración: {best.duration_minutes:.0f} min < {routine_day.target_duration} min objetivo")
        
        return {
            "completed": completed,
            "actual_activity": {
                "id": best.id,
                "name": best.name,
                "distance_km": best.distance_km,
                "duration_minutes": best.duration_minutes
            },
            "reason": "; ".join(reasons) if reasons else "Objetivo cumplido"
        }
    
    def get_weekly_compliance(
        self,
        routine: Routine,
        db: Session,
        week_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get compliance report for a week."""
        week_start, week_end = self.get_week_boundaries(week_date)
        
        # Get all activities for the week
        activities = db.query(Activity).filter(
            Activity.user_id == routine.user_id,
            Activity.start_date >= week_start,
            Activity.start_date < week_end
        ).all()
        
        # Group activities by day of week
        activities_by_day = {}
        for activity in activities:
            day = activity.start_date.weekday()
            if day not in activities_by_day:
                activities_by_day[day] = []
            activities_by_day[day].append(activity)
        
        # Check each routine day
        days_report = []
        completed_count = 0
        
        day_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        
        for routine_day in routine.days:
            day_activities = activities_by_day.get(routine_day.day_of_week, [])
            compliance = self.check_day_compliance(routine_day, day_activities)
            
            if compliance["completed"]:
                completed_count += 1
            
            days_report.append({
                "day_of_week": routine_day.day_of_week,
                "day_name": day_names[routine_day.day_of_week],
                "expected": {
                    "activity_type": routine_day.activity_type,
                    "target_distance": routine_day.target_distance,
                    "target_duration": routine_day.target_duration
                },
                "completed": compliance["completed"],
                "actual_activity": compliance["actual_activity"],
                "reason": compliance["reason"]
            })
        
        total_days = len(routine.days)
        completion_rate = (completed_count / total_days * 100) if total_days > 0 else 0
        
        return {
            "routine_id": routine.id,
            "routine_name": routine.name,
            "week_start": week_start,
            "days": days_report,
            "completion_rate": completion_rate,
            "completed_days": completed_count,
            "total_days": total_days
        }
    
    async def get_missed_activities_today(
        self,
        user: User,
        db: Session
    ) -> List[Dict[str, Any]]:
        """Get routine activities that should have been completed today."""
        today = datetime.utcnow()
        today_weekday = today.weekday()
        
        # Get active routine
        routine = db.query(Routine).filter(
            Routine.user_id == user.id,
            Routine.is_active == True
        ).first()
        
        if not routine:
            return []
        
        # Get today's routine days
        routine_days = db.query(RoutineDay).filter(
            RoutineDay.routine_id == routine.id,
            RoutineDay.day_of_week == today_weekday
        ).all()
        
        if not routine_days:
            return []
        
        # Get today's activities
        today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        today_activities = db.query(Activity).filter(
            Activity.user_id == user.id,
            Activity.start_date >= today_start,
            Activity.start_date < today_end
        ).all()
        
        missed = []
        day_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        
        for routine_day in routine_days:
            compliance = self.check_day_compliance(routine_day, today_activities)
            
            if not compliance["completed"]:
                missed.append({
                    "day_name": day_names[today_weekday],
                    "activity_type": routine_day.activity_type,
                    "target_distance": routine_day.target_distance,
                    "target_duration": routine_day.target_duration,
                    "notes": routine_day.notes
                })
        
        return missed


# Singleton instance
routine_service = RoutineService()
