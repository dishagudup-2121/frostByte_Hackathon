from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend import models

# ✅ MUST create FastAPI app FIRST
app = FastAPI()

@app.get("/")
def root():
    return {"status": "GeoDrive Insight backend running"}

# Analytics endpoint
@app.get("/analytics/sentiment")
def sentiment_by_brand(db: Session = Depends(get_db)):
    result = (
        db.query(
            models.SocialPost.brand,
            models.SocialPost.sentiment,
            func.count().label("count")
        )
        .group_by(models.SocialPost.brand, models.SocialPost.sentiment)
        .all()
    )

    return result
