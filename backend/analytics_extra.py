from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend import models
from datetime import datetime, timedelta

router = APIRouter()



# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def sentiment_trend_timewindow(reviews):
    """Compare last 30 days vs previous 30 days"""
    now = datetime.utcnow()
    last_30 = now - timedelta(days=30)
    prev_60 = now - timedelta(days=60)

    recent = [r for r in reviews if r.created_at >= last_30]
    previous = [r for r in reviews if prev_60 <= r.created_at < last_30]

    def score(data):
        if not data:
            return 0
        return sum(
            1 if r.sentiment == "positive"
            else -1 if r.sentiment == "negative"
            else 0
            for r in data
        ) / len(data)

    r1, r2 = score(recent), score(previous)

    if r1 > r2:
        return "↑ Improving"
    elif r1 < r2:
        return "↓ Declining"
    return "→ Stable"


def ai_feature_gap(c1, c2, company1, company2):
    insights = []

    for f in c1.keys():
        if abs(c1[f] - c2[f]) < 5:
            continue

        if c1[f] > c2[f]:
            insights.append(f"{company1} strong in {f}, {company2} lagging")
        else:
            insights.append(f"{company2} strong in {f}, {company1} lagging")

    return " | ".join(insights)


def recommendation(features):
    best_perf = max(features, key=lambda x: features[x]["performance"])
    best_value = max(features, key=lambda x: features[x]["price"])
    best_overall = max(features, key=lambda x: sum(features[x].values()))

    return {
        "Best Performance": best_perf,
        "Best Value": best_value,
        "Best Overall Sentiment": best_overall
    }

