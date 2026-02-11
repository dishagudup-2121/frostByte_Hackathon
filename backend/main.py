from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from backend.database import get_db, engine
from backend import models
from backend.schemas import SocialPostCreate
from backend.ai_routes import router as ai_router
from backend.analytics_extra import router as extra_router

app = FastAPI()

app.include_router(ai_router, prefix="/ai", tags=["AI"])
app.include_router(extra_router, prefix="/analytics", tags=["Analytics"])


models.Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"status": "GeoDrive Insight backend running"}

@app.post("/posts")
def create_post(post: SocialPostCreate, db: Session = Depends(get_db)):
    db_post = models.SocialPost(
        brand=post.brand,
        text=post.text,
        latitude=post.latitude,
        longitude=post.longitude,
        sentiment=post.sentiment,
        confidence=post.confidence,
        created_at=post.created_at or datetime.utcnow()
    )

    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    return {
        "message": "Post ingested successfully",
        "post_id": db_post.id
    }

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

    return [
        {
            "brand": r.brand,
            "sentiment": r.sentiment,
            "count": r.count
        }
        for r in result
    ]
