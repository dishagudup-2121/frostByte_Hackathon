from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.sql import cast
from sqlalchemy.types import Date
from backend.database import get_db
from backend import models

router = APIRouter()

@router.get("/sentiment")
def sentiment_by_brand(db: Session = Depends(get_db)):
    try:
        result = (
            db.query(
                models.SocialPost.brand,
                models.SocialPost.sentiment,
                func.count().label("count")
            )
            .group_by(
                models.SocialPost.brand,
                models.SocialPost.sentiment
            )
            .all()
        )
        return [
            {"brand": r[0], "sentiment": r[1], "count": r[2]}
            for r in result
        ]
    except Exception as e:
        # 🔴 THIS WILL SHOW THE REAL DB ERROR
        return {
            "error": str(e),
            "hint": "Check column names & table schema"
        }


@router.get("/daily-trend")
def daily_trend(db: Session = Depends(get_db)):
    results = (
        db.query(
            cast(models.SocialPost.created_at, Date).label("date"),
            func.count(models.SocialPost.id).label("total_posts")
        )
        .group_by("date")
        .order_by("date")
        .all()
    )

    return [
        {
            "date": str(r.date),
            "total_posts": r.total_posts
        }
        for r in results
    ]