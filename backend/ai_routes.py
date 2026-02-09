from fastapi import APIRouter
from pydantic import BaseModel
from ai_module.ai_module import analyze_sentiment


router = APIRouter()

class TextInput(BaseModel):
    text: str

@router.post("/analyze")
def analyze_text(payload: TextInput):
    result = analyze_sentiment(payload.text)
    return result
