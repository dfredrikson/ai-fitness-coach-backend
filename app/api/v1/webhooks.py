from fastapi import APIRouter, Query, Depends, BackgroundTasks, HTTPException
from fastapi.requests import Request
from sqlalchemy.orm import Session
import os

from app.core.database import get_db
from app.services import strava_service

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

VERIFY_TOKEN = os.getenv("STRAVA_WEBHOOK_VERIFY_TOKEN", "strava_webhook_token")

@router.get("/strava")
async def verify_webhook(
    mode: str = Query(alias="hub.mode"),
    token: str = Query(alias="hub.verify_token"),
    challenge: str = Query(alias="hub.challenge")
):
    """
    Strava Webhook Subscription Verification.
    """
    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Strava Webhook Verified!")
        return {"hub.challenge": challenge}
    
    raise HTTPException(status_code=403, detail="Invalid verification token")


@router.post("/strava")
async def receive_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Receive Strava Webhook Events.
    """
    event = await request.json()
    
    # Process in background to respond quickly to Strava (timeout < 2s)
    background_tasks.add_task(strava_service.process_webhook_event, event, db)
    
    return {"status": "received"}
