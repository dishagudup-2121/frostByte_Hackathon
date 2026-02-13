import os
import json
import re
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()
client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

# ============================================================
# Known Brands
# ============================================================

KNOWN_BRANDS = {
    "hyundai","toyota","honda","tata","mahindra",
    "bmw","audi","kia","mercedes","ford",
    "skoda","vw","volkswagen","mg","jeep",
    "nissan","renault","suzuki","maruti"
}

AUTO_BRANDS = set()

# ============================================================
# City Coordinates
# ============================================================

CITIES = {
    "mumbai": (19.07, 72.87),
    "pune": (18.52, 73.85),
    "delhi": (28.61, 77.20),
    "bangalore": (12.97, 77.59),
    "chennai": (13.08, 80.27)
}

# ============================================================
# Brand Detection
# ============================================================

def detect_brand(text, ai_brand=None):
    text_lower = text.lower()

    if ai_brand and ai_brand.lower() != "unknown":
        AUTO_BRANDS.add(ai_brand.lower())
        return ai_brand.capitalize()

    for brand in KNOWN_BRANDS.union(AUTO_BRANDS):
        if brand in text_lower:
            return brand.capitalize()

    return "Unknown"

# ============================================================
# Location Extraction
# ============================================================

def extract_location(text):
    text = text.lower()
    for city, coords in CITIES.items():
        if city in text:
            return coords
    return (0.0, 0.0)

# ============================================================
# Sentiment Prompt
# ============================================================

def build_sentiment_prompt(text):
    return f"""
You are an automotive sentiment analysis AI.

Return ONLY valid JSON:

{{
  "brand": "car brand or Unknown",
  "sentiment": "positive|negative|neutral",
  "confidence": 0-1,
  "key_topic": "mileage|engine|service|price|comfort|performance|design|safety|features|resale|availability|customer_support|other"
}}

Text:
{text}
"""

# ============================================================
# Price Fetch Prompt
# ============================================================

def build_price_prompt(model_name):
    return f"""
Provide the current approximate ex-showroom price in India (2026) 
for the car model: {model_name}.

Return ONLY a number in INR.
Example:
1200000
"""

# ============================================================
# Verdict Prompt
# ============================================================

def build_verdict_prompt(model_name, positive_pct, negative_pct):
    return f"""
You are an automotive analyst.

Model: {model_name}
Positive reviews: {positive_pct}%
Negative reviews: {negative_pct}%

Write a short 2-3 line intelligent verdict summary.
Do not mention percentages explicitly.
Sound professional.
"""

# ============================================================
# Safe JSON Parsing
# ============================================================

def safe_json_parse(raw_text):
    try:
        # Extract JSON if wrapped in text
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return json.loads(raw_text)
    except:
        return None

# ============================================================
# Main Sentiment Analysis
# ============================================================

def analyze_sentiment(text: str):

    prompt = build_sentiment_prompt(text)

    try:
        response = client.chat.complete(
            model="mistral-large-latest",
            messages=[{"role": "user", "content": prompt}]
        )

        raw = response.choices[0].message.content
        parsed = safe_json_parse(raw)

        if not parsed:
            raise ValueError("Invalid JSON")

    except Exception:
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

# ============================================================
# Fetch Real Price Using Mistral
# ============================================================

def fetch_model_price(model_name: str):
    try:
        response = client.chat.complete(
            model="mistral-large-latest",
            messages=[{
                "role": "user",
                "content": build_price_prompt(model_name)
            }]
        )

        raw = response.choices[0].message.content.strip()

        # Extract number safely
        number_match = re.search(r"\d+", raw.replace(",", ""))
        if number_match:
            return float(number_match.group())

    except Exception:
        pass

    return 0  # fallback

# ============================================================
# Generate Dynamic Verdict
# ============================================================

def generate_ai_verdict(model_name, positive_pct, negative_pct):
    try:
        response = client.chat.complete(
            model="mistral-large-latest",
            messages=[{
                "role": "user",
                "content": build_verdict_prompt(
                    model_name,
                    positive_pct,
                    negative_pct
                )
            }]
        )

        return response.choices[0].message.content.strip()

    except Exception:
        return "Overall performance appears balanced based on current user feedback."
