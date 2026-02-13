from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import requests
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


@router.post("/analyze")
def analyze_text(request: AnalyzeRequest):

    text = request.text

    result = analyze_sentiment(text)

    extracted_lat = result.get("latitude", 0)
    extracted_lon = result.get("longitude", 0)

    lat = request.latitude if request.latitude is not None else extracted_lat
    lon = request.longitude if request.longitude is not None else extracted_lon

    try:
        requests.post(
            "http://127.0.0.1:8000/posts",
            json={
                "brand": result.get("brand", "Unknown"),
                "text": text,
                "latitude": lat,
                "longitude": lon,
                "sentiment": result.get("sentiment", "neutral"),
                "confidence": result.get("confidence", 0.5)
            },
            timeout=5
        )
    except Exception as e:
        print("DB POST failed:", e)

    return {
        **result,
        "latitude": lat,
        "longitude": lon
    }



@router.post("/analyze-product")
def analyze_product(request: AnalyzeRequest, db: Session = Depends(get_db)):

    text = request.text.lower()


    all_products = db.query(models.Product).all()
    product = None

    for p in all_products:
        model_words = p.model_name.lower().split()
        if any(word in text for word in model_words):
            product = p
            break

    if not product:
        raise HTTPException(status_code=404, detail="Product not found in DB")

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

    price_data = db.query(models.PriceHistory).filter(
        models.PriceHistory.product_id == product.id
    ).all()

    price_history = [
        {"month": p.month, "price": p.price}
        for p in price_data
    ]

    availability_data = db.query(models.Availability).filter(
        models.Availability.product_id == product.id
    ).all()

    availability = [
        {"region": a.region, "available": a.available}
        for a in availability_data
    ]

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
