from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from backend.database import get_db
from backend import models
from backend.schemas import SocialPostCreate

router = APIRouter()

@router.post("/")
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
