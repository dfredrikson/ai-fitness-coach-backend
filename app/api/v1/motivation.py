@router.get("/daily")
def get_daily_motivation(db: Session = Depends(get_db)):
    msg = db.query(DailyMotivation)\
        .order_by(DailyMotivation.date.desc())\
        .first()

    if not msg:
        return {"message": None}

    return {"message": msg.message}

@router.get("/latest-activity")
def get_latest_activity_motivation(db: Session = Depends(get_db)):
    msg = db.query(ActivityMotivation)\
        .order_by(ActivityMotivation.created_at.desc())\
        .first()

    if not msg:
        return {"message": None}

    return {"message": msg.message}

