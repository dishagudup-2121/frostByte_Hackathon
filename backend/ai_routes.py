from fastapi import APIRouter
from pydantic import BaseModel
import requests
from ai_module.ai_module import analyze_sentiment

router = APIRouter()

# Request model (clean Swagger + validation)
class AnalyzeRequest(BaseModel):
    text: str


@router.post("/analyze")
def analyze_text(request: AnalyzeRequest):
    text = request.text

    # Call AI module
    result = analyze_sentiment(text)

    # Send to Person 1 ingestion endpoint
    try:
        requests.post(
            "http://127.0.0.1:8000/posts",
            json={
                "brand": result.get("brand", "Unknown"),
                "text": text,
                "latitude": result.get("latitude", 0),
                "longitude": result.get("longitude", 0),
                "sentiment": result.get("sentiment", "neutral"),
                "confidence": result.get("confidence", 0.5)
            },
            timeout=5
        )
    except Exception as e:
        print("DB POST failed:", e)

    return result
