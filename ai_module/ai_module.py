import os
import json
import sqlite3
import requests
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=api_key)

# SQLite DB for local logging
conn = sqlite3.connect("sentiment.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS sentiment_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sentiment TEXT,
    confidence REAL,
    key_topic TEXT
)
""")
conn.commit()


def save_result(result: dict):
    cursor.execute(
        "INSERT INTO sentiment_results (sentiment, confidence, key_topic) VALUES (?, ?, ?)",
        (result["sentiment"], result["confidence"], result["key_topic"])
    )
    conn.commit()


def analyze_sentiment(text: str) -> dict:
    response = client.chat.complete(
        model="mistral-large-latest",
        messages=[
            {
                "role": "user",
                "content": f"""
Analyze automotive sentiment from this text.
Return ONLY valid JSON (no markdown, no explanation):

{{
  "sentiment": "positive/negative/neutral",
  "confidence": 0-1,
  "key_topic": "main automotive issue"
}}

Text: {text}
"""
            }
        ]
    )

    output = response.choices[0].message.content.strip()

    # Remove markdown safely if present
    if "```" in output:
        parts = output.split("```")
        if len(parts) > 1:
            output = parts[1].replace("json", "").strip()

    # Parse safely
    try:
        parsed = json.loads(output)
    except Exception:
        parsed = {
            "sentiment": "unknown",
            "confidence": 0.0,
            "key_topic": "parse_error"
        }

    # Enforce consistent schema
    result = {
        "sentiment": str(parsed.get("sentiment", "unknown")).lower(),
        "confidence": float(parsed.get("confidence", 0)),
        "key_topic": str(parsed.get("key_topic", "unknown"))
    }
    result["confidence"] = max(0.0, min(1.0, float(result["confidence"])))

    if result["sentiment"] not in ["positive", "negative", "neutral"]:
      result["sentiment"] = "neutral"

    save_result(result)
    return result


brands = ["hyundai", "toyota", "honda", "tata", "mahindra"]

def detect_brand(text):
    text = text.lower()
    for b in brands:
        if b in text:
            return b.capitalize()
    return "Unknown"
def extract_location(text):
    cities = {
        "mumbai": (19.07, 72.87),
        "pune": (18.52, 73.85),
        "delhi": (28.61, 77.20)
    }

    text = text.lower()
    for city, coords in cities.items():
        if city in text:
            return coords
    return (0.0, 0.0)

def categorize_topic(topic):
    topic = topic.lower()
    if "mile" in topic: return "Mileage"
    if "engine" in topic: return "Engine"
    if "comfort" in topic: return "Comfort"
    if "service" in topic: return "Service"
    return "Other"



# Local test + backend push
if __name__ == "__main__":
    text = "Mileage is very poor Hyundai car"   # text FIRST
    brand = detect_brand(text)  
    lat, lon = extract_location(text)                # then detect brand

    result = analyze_sentiment(text)
    print(result)

    try:
        requests.post(
            "http://127.0.0.1:8000/posts",
            json={
                "brand": brand,
                "text": text,
                "latitude": lat,
                "longitude": lon,
                "sentiment": result["sentiment"],
                "confidence": result["confidence"]
            },
            timeout=10
        )
    except Exception as e:
        print("Backend POST failed:", e)
