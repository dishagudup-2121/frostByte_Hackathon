from fastapi import APIRouter, Depends, HTTPException
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
            func.count(models.SocialPost.id).label("total_posts")
        )
        .group_by(models.SocialPost.brand)
        .all()
    )

    return [
        {
            "brand": r.brand,
            "total_posts": r.total_posts
        }
        for r in result
    ]


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


@router.get("/company-summary/{company}")
def company_summary(company: str, db: Session = Depends(get_db)):

    products = db.query(models.Product).filter(
        func.lower(models.Product.company) == company.lower()
    ).all()

    if not products:
        raise HTTPException(status_code=404, detail="Company not found")

    product_ids = [p.id for p in products]

    total_reviews = db.query(models.Review).filter(
        models.Review.product_id.in_(product_ids)
    ).count()

    positive_reviews = db.query(models.Review).filter(
        models.Review.product_id.in_(product_ids),
        models.Review.sentiment == "positive"
    ).count()

    overall_positive_percent = (
        int((positive_reviews / total_reviews) * 100)
        if total_reviews else 0
    )

    model_scores = []

    for p in products:
        pos = db.query(models.Review).filter(
            models.Review.product_id == p.id,
            models.Review.sentiment == "positive"
        ).count()

        total = db.query(models.Review).filter(
            models.Review.product_id == p.id
        ).count()

        score = (pos / total) if total else 0
        model_scores.append((p.model_name, score))

    model_scores.sort(key=lambda x: x[1], reverse=True)

    best_model = model_scores[0][0] if model_scores else None
    worst_model = model_scores[-1][0] if model_scores else None

    return {
        "company": company,
        "total_products": len(products),
        "total_reviews": total_reviews,
        "overall_positive_percent": overall_positive_percent,
        "best_model": best_model,
        "worst_model": worst_model
    }
