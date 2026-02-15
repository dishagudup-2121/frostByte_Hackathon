from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend import models
from backend.analytics_extra import (
    ai_feature_gap,
    sentiment_trend_timewindow,
    recommendation
)

router = APIRouter()

# -----------------------------
# BRAND SUMMARY
# -----------------------------
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

    return [{"brand": r.brand, "total_posts": r.total_posts} for r in result]


# -----------------------------
# MARKET SENTIMENT SHARE
# -----------------------------
@router.get("/market-sentiment-share")
def market_sentiment_share(db: Session = Depends(get_db)):

    results = (
        db.query(
            models.Product.company.label("brand"),
            func.count(models.Review.id).label("positive_count")
        )
        .join(models.Review, models.Review.product_id == models.Product.id)
        .filter(func.lower(models.Review.sentiment) == "positive")
        .group_by(models.Product.company)
        .all()
    )

    total_positive = sum(r.positive_count for r in results) or 1

    return [
        {
            "brand": r.brand,
            "sentiment_share": round((r.positive_count / total_positive) * 100, 2)
        }
        for r in results
    ]






@router.get("/feature-comparison")

def feature_comparison(company1: str, company2: str, db: Session = Depends(get_db)):

    features = {
        "price": ["price", "cost", "expensive", "affordable", "value"],
        "comfort": ["comfort", "seat", "interior"],
        "performance": ["performance", "power", "engine", "speed"],
        "mileage": ["mileage", "fuel", "economy"]
    }

    def analyze(company):
        results = {f: 0 for f in features}

        reviews = (
            db.query(models.Review.comment, models.Review.sentiment)
            .join(models.Product, models.Product.id == models.Review.product_id)
            .filter(func.lower(models.Product.company) == company.lower())
            .all()
        )

        for comment, sentiment in reviews:
            if sentiment != "positive":
                continue

            text = comment.lower()
            for f, words in features.items():
                if any(w in text for w in words):
                    results[f] += 1

        total = sum(results.values()) or 1
        return {f: round((v / total) * 100, 1) for f, v in results.items()}

    c1 = analyze(company1)
    c2 = analyze(company2)

    # Trend per company
    reviews_c1 = (
        db.query(models.Review)
        .join(models.Product, models.Product.id == models.Review.product_id)
        .filter(func.lower(models.Product.company) == company1.lower())
        .all()
    )

    reviews_c2 = (
        db.query(models.Review)
        .join(models.Product, models.Product.id == models.Review.product_id)
        .filter(func.lower(models.Product.company) == company2.lower())
        .all()
    )

    trend = {
        company1: sentiment_trend_timewindow(reviews_c1),
        company2: sentiment_trend_timewindow(reviews_c2),
    }

    feature_data = {
        company1: c1,
        company2: c2
    }

    rec = recommendation(feature_data)
    ai_insight = ai_feature_gap(c1, c2, company1, company2)

    return {
        "company1": company1,
        "company2": company2,
        "features1": c1,
        "features2": c2,
        "ai_insight": ai_insight,
        "trend": trend,
        "recommendation": rec
    }
