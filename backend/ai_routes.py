from fastapi import APIRouter
from pydantic import BaseModel
from ai_module.ai_module import analyze_sentiment, detect_brand, extract_location

router = APIRouter()

class TextInput(BaseModel):
    text: str

@router.post("/analyze")
def analyze_text(payload: TextInput):
    text = payload.text

    result = analyze_sentiment(text)
    brand = detect_brand(text)
    lat, lon = extract_location(text)

    return {
        "brand": brand,
        "latitude": lat,
        "longitude": lon,
        **result
    }
