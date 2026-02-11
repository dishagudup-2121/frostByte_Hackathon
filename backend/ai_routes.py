from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import requests
from ai_module.ai_module import analyze_sentiment

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
