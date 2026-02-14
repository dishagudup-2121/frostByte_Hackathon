from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend import models
from ai_module.ai_module import (
    analyze_sentiment,
    fetch_model_price,
    generate_ai_verdict
)
from collections import Counter
import re

router = APIRouter()

# =========================
# Request Model
# =========================
class AnalyzeRequest(BaseModel):
    text: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

# ============================================================
# 1️⃣ SENTIMENT + AUTO PRODUCT CREATION (SMART PRICE)
# ============================================================
@router.post("/analyze")
def analyze_text(request: AnalyzeRequest, db: Session = Depends(get_db)):

    text = request.text
    text_lower = text.lower()

    result = analyze_sentiment(text)

    brand = result.get("brand", "Unknown")
    sentiment = result.get("sentiment", "neutral")
    confidence = result.get("confidence", 0.5)

    lat = request.latitude
    lon = request.longitude

    # Insert into social_posts
    new_post = models.SocialPost(
        brand=brand,
        text=text,
        latitude=lat,
        longitude=lon,
        sentiment=sentiment,
        confidence=confidence
    )
    db.add(new_post)

    # 🔍 Try product match
    product = db.query(models.Product).filter(
        func.lower(models.Product.model_name).contains(text_lower)
    ).first()

    # 🔥 Auto create with REAL PRICE
    if not product and brand != "Unknown":
        words = text.split()
        model_name = " ".join(words[:2]).title()

        real_price = fetch_model_price(model_name)

        product = models.Product(
            model_name=model_name,
            company=brand.title(),
            current_price=real_price
        )
        db.add(product)
        db.flush()

    # Insert review
    if product:
        new_review = models.Review(
            product_id=product.id,
            comment=text,
            sentiment=sentiment,
            confidence=confidence
        )
        db.add(new_review)

    db.commit()

    return {
        **result,
        "latitude": lat,
        "longitude": lon
    }

# ============================================================
# 2️⃣ DEEP SCAN WITH AGGREGATED FINGERPRINT + AI VERDICT
# ============================================================
@router.post("/analyze-product")
def analyze_product(request: AnalyzeRequest, db: Session = Depends(get_db)):

    text = request.text.lower()

    product = db.query(models.Product).filter(
        func.lower(models.Product.model_name).contains(text)
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    reviews_query = db.query(models.Review).filter(
        models.Review.product_id == product.id
    )

    total_reviews = reviews_query.count()

    positive = reviews_query.filter(
        models.Review.sentiment == "positive"
    ).count()

    negative = reviews_query.filter(
        models.Review.sentiment == "negative"
    ).count()

    confidence_avg = db.query(func.avg(models.Review.confidence)).filter(
        models.Review.product_id == product.id
    ).scalar() or 0

    sentiment_summary = {
        "positive_percent": int((positive / total_reviews) * 100) if total_reviews else 0,
        "negative_percent": int((negative / total_reviews) * 100) if total_reviews else 0,
        "confidence": round(float(confidence_avg), 2)
    }

    # ========================================================
    # 🔥 SMART FINGERPRINT (Topic Aggregation)
    # ========================================================

    reviews = reviews_query.all()

    topic_counter = Counter()

    for review in reviews:
        topic_result = analyze_sentiment(review.comment)
        topic = topic_result.get("key_topic", "other")
        topic_counter[topic] += 1

    fingerprint = []
    for topic, count in topic_counter.items():
        percentage = int((count / total_reviews) * 100) if total_reviews else 0
        fingerprint.append({
            "topic": topic,
            "strength": percentage
        })

    # ========================================================
    # 🔥 AI VERDICT (Correct way)
    # ========================================================

    verdict = "Not enough data for verdict."

    if total_reviews > 0:
        verdict = generate_ai_verdict(
            product.model_name,
            sentiment_summary["positive_percent"],
            sentiment_summary["negative_percent"]
        )

    # ========================================================
    # Return Data
    # ========================================================

    return {
        "product_id": product.id,
        "model_name": product.model_name,
        "company": product.company,
        "current_price": product.current_price,
        "sentiment_summary": sentiment_summary,
        "fingerprint": fingerprint,
        "total_reviews": total_reviews,
        "ai_verdict": verdict
    }
