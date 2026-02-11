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

@router.get("/location-summary")
def location_summary(db: Session = Depends(get_db)):
    results = (
        db.query(
            models.SocialPost.latitude,
            models.SocialPost.longitude,
            func.count(models.SocialPost.id).label("total_posts")
        )
        .group_by(
            models.SocialPost.latitude,
            models.SocialPost.longitude
        )
        .all()
    )

    return [
        {
            "latitude": r.latitude,
            "longitude": r.longitude,
            "total_posts": r.total_posts
        }
        for r in results
    ]

