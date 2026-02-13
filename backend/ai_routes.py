from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import requests
from ai_module.ai_module import analyze_sentiment


from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import Depends, HTTPException
from backend.database import get_db
from backend import models

router = APIRouter()

# Updated Request model
class AnalyzeRequest(BaseModel):
    text: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


@router.post("/analyze")
def analyze_text(request: AnalyzeRequest):

    text = request.text

    # Call AI module
    result = analyze_sentiment(text)

    # Extract AI-based location
    extracted_lat = result.get("latitude", 0)
    extracted_lon = result.get("longitude", 0)

    # Override with device location if provided
    lat = request.latitude if request.latitude is not None else extracted_lat
    lon = request.longitude if request.longitude is not None else extracted_lon

    # Send to ingestion endpoint
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

    # Return AI result (with final lat/lon used)
    return {
        **result,
        "latitude": lat,
        "longitude": lon
    }



@router.post("/analyze-product")
def analyze_product(request: AnalyzeRequest, db: Session = Depends(get_db)):

    text = request.text.lower()

    # Basic product detection (match model_name inside text)
    all_products = db.query(models.Product).all()

    product = None
    for p in all_products:
        if p.model_name.lower() in text:
            product = p
            break


    if not product:
        raise HTTPException(status_code=404, detail="Product not found in DB")

    # Sentiment aggregation
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

    # Review volume trend
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

    sentiment_summary = {
        "positive": int((positive / total_reviews) * 100) if total_reviews else 0,
        "negative": int((negative / total_reviews) * 100) if total_reviews else 0,
        "confidence": round(float(confidence_avg), 2)
    }

    return {
        "product_id": product.id,
        "model_name": product.model_name,
        "company": product.company,
        "current_price": product.current_price,
        "price_history": price_history,
        "availability_by_region": availability,
        "sentiment_summary": sentiment_summary,
        "top_topics": [   # temporary mock
            {"topic": "mileage", "count": 20},
            {"topic": "price", "count": 15}
        ],
        "review_volume_trend": review_volume_trend
    }
