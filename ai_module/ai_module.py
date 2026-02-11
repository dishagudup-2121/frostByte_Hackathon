import os
import json
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()
client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

# Known brands fallback
KNOWN_BRANDS = {
    "hyundai","toyota","honda","tata","mahindra",
    "bmw","audi","kia","mercedes","ford",
    "skoda","vw","volkswagen","mg","jeep",
    "nissan","renault","suzuki","maruti"
}

# Auto‑learned brands
AUTO_BRANDS = set()

# Cities → coordinates
CITIES = {
    "mumbai": (19.07, 72.87),
    "pune": (18.52, 73.85),
    "delhi": (28.61, 77.20),
    "bangalore": (12.97, 77.59),
    "chennai": (13.08, 80.27)
}


# -------- Brand Detection --------
def detect_brand(text, ai_brand=None):
    text_lower = text.lower()

    # Prefer AI-detected brand
    if ai_brand and ai_brand.lower() != "unknown":
        AUTO_BRANDS.add(ai_brand.lower())
        return ai_brand.capitalize()

    # Fallback keyword detection
    for brand in KNOWN_BRANDS.union(AUTO_BRANDS):
        if brand in text_lower:
            return brand.capitalize()

    return "Unknown"


# -------- Location Extraction --------
def extract_location(text):
    text = text.lower()
    for city, coords in CITIES.items():
        if city in text:
            return coords
    return (0.0, 0.0)


# -------- Prompt Builder --------
def build_prompt(text):
    return f"""
You are an automotive sentiment analysis AI.

Return ONLY JSON:

{{
  "brand": "car brand or Unknown",
  "sentiment": "positive|negative|neutral",
  "confidence": 0-1,
  "key_topic": 
"mileage|engine|service|price|comfort|performance|
 design|safety|features|resale|availability|
 customer_support|other"

}}

Rules:
- Praise → positive
- Complaints (cost, poor mileage, bad service) → negative
- Neutral info/news → neutral
- Always choose ONE topic.

Text:
{text}
"""


# -------- Main Analysis Function --------
def analyze_sentiment(text: str):

    prompt = build_prompt(text)

    try:
        response = client.chat.complete(
            model="mistral-large-latest",
            messages=[{"role": "user", "content": prompt}]
        )

        raw = response.choices[0].message.content
        parsed = json.loads(raw)

    except Exception:
        # Safe fallback if AI fails
        parsed = {
            "brand": "Unknown",
            "sentiment": "neutral",
            "confidence": 0.5,
            "key_topic": "other"
        }

    lat, lon = extract_location(text)



    return {
        "brand": detect_brand(text, parsed.get("brand")),
        "latitude": lat,
        "longitude": lon,
        "sentiment": parsed.get("sentiment", "neutral"),
        "confidence": float(parsed.get("confidence", 0.5)),
        "key_topic": parsed.get("key_topic", "other")
    }
