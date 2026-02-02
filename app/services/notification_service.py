"""
AI Fitness Coach - Notification Service
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.models.user import User


class NotificationService:
    """Service for handling notifications."""
    
    async def create_notification(
        self,
        db: Session,
        user: User,
        type: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Notification:
        """Create a new notification and attempt to send push."""
        
        notification = Notification(
            user_id=user.id,
            type=type,
            title=title,
            body=body,
            data=data or {}
        )
        
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        # TODO: Trigger Push Notification here
        # await self._send_push_notification(user, notification)
        
        return notification
    
    def get_unread_notifications(self, db: Session, user_id: str) -> List[Notification]:
        """Get all unread notifications for a user."""
        return db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).order_by(Notification.created_at.desc()).all()
        
    def mark_as_read(self, db: Session, notification_id: str, user_id: str) -> bool:
        """Mark a notification as read."""
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if notification:
            notification.is_read = True
            db.commit()
            return True
        return False

    async def _send_push_notification(self, user: User, notification: Notification):
        """
        Placeholder for sending push notification using WebPush / VAPID.
        To be implemented when Push logic is added.
        """
        pass


# Singleton instance
notification_service = NotificationService()
