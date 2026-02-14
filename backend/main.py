from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from backend.database import get_db, engine
from backend import models
from backend.schemas import SocialPostCreate
from backend.ai_routes import router as ai_router
from backend.analytics_extra import router as extra_router
from fastapi.middleware.cors import CORSMiddleware

# ============================================================
# APP INIT
# ============================================================
print("Creating tables...")
models.Base.metadata.create_all(bind=engine)
print("Tables created.")

app = FastAPI(title="GeoDrive Insight API")

app.include_router(ai_router, prefix="/ai", tags=["AI"])
app.include_router(extra_router, prefix="/analytics", tags=["Analytics"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {"status": "GeoDrive Insight backend running 🚀"}


# ============================================================
# CREATE SOCIAL POST
# ============================================================

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


# ============================================================
# BRAND SENTIMENT SUMMARY
# ============================================================

@app.get("/sentiment")
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


# ============================================================
# GET ALL POSTS (FOR MAP PERSISTENCE)
# ============================================================

@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.SocialPost).all()

    return [
        {
            "id": p.id,
            "brand": p.brand,
            "latitude": p.latitude,
            "longitude": p.longitude,
            "sentiment": p.sentiment,
            "confidence": p.confidence,
            "created_at": p.created_at
        }
        for p in posts
    ]


# ============================================================
# 🔥 NEW: REVIEW LOCATION ENDPOINT (Better Than /posts)
# ============================================================

@app.get("/analytics/review-locations")
def review_locations(db: Session = Depends(get_db)):
    reviews = db.query(models.Review).filter(
        models.Review.latitude.isnot(None),
        models.Review.longitude.isnot(None)
    ).all()

    return [
        {
            "brand": r.brand,
            "latitude": r.latitude,
            "longitude": r.longitude,
            "sentiment": r.sentiment
        }
        for r in reviews
    ]


# ============================================================
# 🔥 NEW: COMPANY SUMMARY (for Company Insights Card)
# ============================================================

@app.get("/analytics/company-summary/{company}")
def company_summary(company: str, db: Session = Depends(get_db)):

    total_models = db.query(models.Product).filter(
        func.lower(models.Product.company) == company.lower()
    ).count()

    product_ids = db.query(models.Product.id).filter(
        func.lower(models.Product.company) == company.lower()
    ).subquery()

    total_reviews = db.query(models.Review).filter(
        models.Review.product_id.in_(product_ids)
    ).count()

    positive_reviews = db.query(models.Review).filter(
        models.Review.product_id.in_(product_ids),
        models.Review.sentiment == "positive"
    ).count()

    positive_percent = int((positive_reviews / total_reviews) * 100) if total_reviews else 0

    return {
        "company": company.title(),
        "total_models": total_models,
        "total_reviews": total_reviews,
        "overall_positive_percent": positive_percent
    }