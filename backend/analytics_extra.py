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

@router.get("/brand-sentiment-ratio")
def brand_sentiment_ratio(db: Session = Depends(get_db)):
    results = (
        db.query(
            models.SocialPost.brand,
            models.SocialPost.sentiment,
            func.count(models.SocialPost.id).label("count")
        )
        .group_by(
            models.SocialPost.brand,
            models.SocialPost.sentiment
        )
        .all()
    )

    data = {}

    for r in results:
        if r.brand not in data:
            data[r.brand] = {
                "brand": r.brand,
                "positive": 0,
                "negative": 0,
                "neutral": 0
            }

        data[r.brand][r.sentiment] = r.count

    return list(data.values())
