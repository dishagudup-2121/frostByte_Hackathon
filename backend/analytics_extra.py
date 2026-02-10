from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend import models

router = APIRouter()

@router.get("/brand-summary")
def brand_summary(db: Session = Depends(get_db)):
    result = (
        db.query(
            models.SocialPost.brand,
            func.count().label("total")
        )
        .group_by(models.SocialPost.brand)
        .all()
    )

    return [{"brand": r.brand, "total_posts": r.total} for r in result]
