# ai_module/ai_module.py

import os
import json
from typing import Dict
from mistralai import Mistral
from dotenv import load_dotenv

# --------------------------------------------------
# Load environment variables
# --------------------------------------------------
load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

if not MISTRAL_API_KEY:
    print("⚠️ WARNING: MISTRAL_API_KEY not set. AI disabled.")
    client = None


client = Mistral(api_key=MISTRAL_API_KEY)

# --------------------------------------------------
# Brand detection (simple & fast)
# --------------------------------------------------
KNOWN_BRANDS = [
    "hyundai", "tata", "mahindra", "toyota",
    "honda", "suzuki", "kia", "bmw", "audi"
]

def detect_brand(text: str) -> str:
    text_lower = text.lower()
    for brand in KNOWN_BRANDS:
        if brand in text_lower:
            return brand.capitalize()
    return "Unknown"

# --------------------------------------------------
# Location detection (basic keyword mapping)
# --------------------------------------------------
CITY_COORDS = {
    "pune": (18.5204, 73.8567),
    "mumbai": (19.0760, 72.8777),
    "bangalore": (12.9716, 77.5946),
    "delhi": (28.6139, 77.2090),
    "chennai": (13.0827, 80.2707)
}

def detect_location(text: str):
    text_lower = text.lower()
    for city, coords in CITY_COORDS.items():
        if city in text_lower:
            return coords
    return (None, None)

# --------------------------------------------------
# Core AI function (PURE FUNCTION)
# --------------------------------------------------
def analyze_sentiment(text: str) -> Dict:
    
    if client is None:
        return {
            "brand": "Unknown",
            "latitude": None,
            "longitude": None,
            "sentiment": "unknown",
            "confidence": 0.0,
            "key_topic": "api_key_missing"
        }

    
    """
    PURE AI FUNCTION
    - No database
    - No network except Mistral
    - Safe to import in FastAPI
    """

    response = client.chat.complete(
        model="mistral-large-latest",
        messages=[
            {
                "role": "user",
                "content": f"""
Analyze the automotive sentiment of the following text.

Return ONLY valid JSON (no markdown, no explanation):

{{
  "sentiment": "positive | negative | neutral",
  "confidence": 0.0-1.0,
  "key_topic": "main automotive issue"
}}

Text:
{text}
"""
            }
        ]
    )

    raw_output = response.choices[0].message.content.strip()

    # Safety: strip markdown if model adds it
    if "```" in raw_output:
        raw_output = raw_output.replace("```json", "").replace("```", "").strip()

    try:
        ai_result = json.loads(raw_output)
    except Exception:
        ai_result = {
            "sentiment": "unknown",
            "confidence": 0.0,
            "key_topic": "parse_error"
        }

    # Enforce schema
    sentiment = str(ai_result.get("sentiment", "unknown")).lower()
    confidence = float(ai_result.get("confidence", 0.0))
    key_topic = str(ai_result.get("key_topic", "unknown"))

    brand = detect_brand(text)
    latitude, longitude = detect_location(text)

    return {
        "brand": brand,
        "latitude": latitude,
        "longitude": longitude,
        "sentiment": sentiment,
        "confidence": confidence,
        "key_topic": key_topic
    }

# --------------------------------------------------
# Optional local test (SAFE)
# --------------------------------------------------
if __name__ == "__main__":
    sample_text = "Hyundai mileage is very poor in Pune"
    result = analyze_sentiment(sample_text)
    print(json.dumps(result, indent=2))
