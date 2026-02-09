# ai_module.py
import os
import json
import sqlite3
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=api_key)

# DB connection
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
Return ONLY JSON:

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

    output = response.choices[0].message.content
    output = output.replace("```json", "").replace("```", "").strip()

    try:
        result = json.loads(output)
    except json.JSONDecodeError:
        result = {
            "sentiment": "unknown",
            "confidence": 0,
            "key_topic": "parse_error"
        }

    save_result(result)
    return result
