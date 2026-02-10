import os
import json
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()
client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

# Expanded brand list
BRANDS = [
    "hyundai","toyota","honda","tata","mahindra",
    "bmw","audi","kia","mercedes","ford","skoda"
]

# Expanded location list
CITIES = {
    "mumbai": (19.07, 72.87),
    "pune": (18.52, 73.85),
    "delhi": (28.61, 77.20),
    "bangalore": (12.97, 77.59),
    "chennai": (13.08, 80.27)
}

def detect_brand(text: str):
    text = text.lower()
    for b in BRANDS:
        if b in text:
            return b.capitalize()
    return "Unknown"

def extract_location(text):
    text = text.lower()
    for city, coords in CITIES.items():
        if city in text:
            return coords
    return (0.0, 0.0)

def analyze_sentiment(text: str):
    prompt = f"""
You are an automotive sentiment AI.

Analyze this car-related text and return ONLY valid JSON:

{{
  "sentiment": "positive/negative/neutral",
  "confidence": 0-1,
  "key_topic": "mileage/engine/service/design/price/comfort/other"
}}

Rules:
- Mileage complaints → negative
- Praise → positive
- Neutral info → neutral

Text: {text}
"""

    response = client.chat.complete(
        model="mistral-large-latest",
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        parsed = json.loads(response.choices[0].message.content)
    except Exception:
        parsed = {}

    lat, lon = extract_location(text)

    return {
        "brand": detect_brand(text),
        "latitude": lat,
        "longitude": lon,
        "sentiment": parsed.get("sentiment", "neutral"),
        "confidence": float(parsed.get("confidence", 0.7)),
        "key_topic": parsed.get("key_topic", "other")
    }
