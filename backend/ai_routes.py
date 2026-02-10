from fastapi import APIRouter
import requests
from ai_module.ai_module import analyze_sentiment

router = APIRouter()

@router.post("/analyze")
def analyze_text(data: dict):
    text = data.get("text")

    result = analyze_sentiment(text)

    # SAFE access (prevents KeyError)
    brand = result.get("brand", "Unknown")
    latitude = result.get("latitude", 0)
    longitude = result.get("longitude", 0)
    sentiment = result.get("sentiment", "neutral")
    confidence = result.get("confidence", 0.5)

    # Send to DB ingestion API
    try:
        requests.post(
            "http://127.0.0.1:8000/posts",
            json={
                "brand": brand,
                "text": text,
                "latitude": latitude,
                "longitude": longitude,
                "sentiment": sentiment,
                "confidence": confidence
            },
            timeout=3
        )
    except Exception as e:
        print("DB POST error:", e)

    return result
