from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from backend.database import get_db, engine
from backend import models
from backend.schemas import SocialPostCreate

# ✅ Create FastAPI app FIRST
app = FastAPI()

# ✅ Create tables once at startup
models.Base.metadata.create_all(bind=engine)

# -----------------------
# Health check
# -----------------------
@app.get("/")
def root():
    return {"status": "GeoDrive Insight backend running"}

# -----------------------
# Ingestion API (Person 1)
# -----------------------
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

# -----------------------
# Analytics API (Person 2)
# -----------------------
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
