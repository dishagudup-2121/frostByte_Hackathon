from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend import models
from ai_module.ai_module import analyze_sentiment
from collections import Counter
import re

router = APIRouter()

class AnalyzeRequest(BaseModel):
    text: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


# ============================================================
# 1️⃣ SENTIMENT + AUTO PRODUCT CREATION (FIXED VERSION)
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

    # 1️⃣ Insert into social_posts
    new_post = models.SocialPost(
        brand=brand,
        text=text,
        latitude=lat,
        longitude=lon,
        sentiment=sentiment,
        confidence=confidence
    )
    db.add(new_post)

    # 2️⃣ Try exact model match first (VERY IMPORTANT)
    product = db.query(models.Product).filter(
        func.lower(models.Product.model_name) == text_lower
    ).first()

    # 3️⃣ If not exact, try partial match
    if not product:
        product = db.query(models.Product).filter(
            func.lower(models.Product.model_name).contains(text_lower)
        ).first()

    # 4️⃣ If still not found → create new model using first 2 words
    if not product and brand != "Unknown":
        words = text.split()

        # Extract model name smartly
        if len(words) >= 2:
            model_name = f"{words[0]} {words[1]}"
        else:
            model_name = f"{brand} Model"

        product = models.Product(
            model_name=model_name.title(),
            company=brand.title(),
            current_price=0
        )
        db.add(product)
        db.flush()

    # 5️⃣ Insert into reviews
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
# 2️⃣ DEEP SCAN (IMPROVED MATCHING)
# ============================================================
@router.post("/analyze-product")
def analyze_product(request: AnalyzeRequest, db: Session = Depends(get_db)):

    text = request.text.lower()

    # 🔥 Match by full model name first
    product = db.query(models.Product).filter(
        func.lower(models.Product.model_name).contains(text)
    ).first()

    # 🔥 If not found, try matching individual words
    if not product:
        words = text.split()
        for word in words:
            product = db.query(models.Product).filter(
                func.lower(models.Product.model_name).contains(word)
            ).first()
            if product:
                break

    if not product:
        raise HTTPException(status_code=404, detail="Product not found in DB")

    # =============================
    # Analytics
    # =============================

    total_reviews = db.query(models.Review).filter(
        models.Review.product_id == product.id
    ).count()

    positive = db.query(models.Review).filter(
        models.Review.product_id == product.id,
        models.Review.sentiment == "positive"
    ).count()

    negative = db.query(models.Review).filter(
        models.Review.product_id == product.id,
        models.Review.sentiment == "negative"
    ).count()

    confidence_avg = db.query(func.avg(models.Review.confidence)).filter(
        models.Review.product_id == product.id
    ).scalar() or 0

    sentiment_summary = {
        "positive": int((positive / total_reviews) * 100) if total_reviews else 0,
        "negative": int((negative / total_reviews) * 100) if total_reviews else 0,
        "confidence": round(float(confidence_avg), 2)
    }

    # Price history
    price_data = db.query(models.PriceHistory).filter(
        models.PriceHistory.product_id == product.id
    ).all()

    price_history = [
        {"month": p.month, "price": p.price}
        for p in price_data
    ]

    # Availability
    availability_data = db.query(models.Availability).filter(
        models.Availability.product_id == product.id
    ).all()

    availability = [
        {"region": a.region, "available": a.available}
        for a in availability_data
    ]

    # Review trend
    review_trend_raw = db.query(
        func.to_char(models.Review.created_at, 'Mon').label("month"),
        func.count(models.Review.id).label("count")
    ).filter(
        models.Review.product_id == product.id
    ).group_by("month").all()

    review_volume_trend = [
        {"month": r.month, "count": r.count}
        for r in review_trend_raw
    ]

    # Top topics
    reviews = db.query(models.Review.comment).filter(
        models.Review.product_id == product.id
    ).all()

    all_text = " ".join([r[0] for r in reviews]).lower()
    words = re.findall(r'\b[a-z]{4,}\b', all_text)

    stopwords = {
        "this", "that", "with", "have", "very", "good",
        "nice", "from", "they", "will", "your", "about",
        "there", "which", "their"
    }

    filtered_words = [w for w in words if w not in stopwords]
    word_counts = Counter(filtered_words).most_common(5)

    top_topics = [
        {"topic": word, "count": count}
        for word, count in word_counts
    ]

    return {
        "product_id": product.id,
        "model_name": product.model_name,
        "company": product.company,
        "current_price": product.current_price,
        "price_history": price_history,
        "availability_by_region": availability,
        "sentiment_summary": sentiment_summary,
        "top_topics": top_topics,
        "review_volume_trend": review_volume_trend
    }
