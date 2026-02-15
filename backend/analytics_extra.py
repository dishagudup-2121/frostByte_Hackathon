from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend import models
<<<<<<< HEAD
from datetime import datetime
=======
from datetime import datetime, timedelta
>>>>>>> c808026291fc235df6d0142b54f66f2780db5386

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

<<<<<<< HEAD



@router.get("/company-summary/{company}")
def company_summary(company: str, db: Session = Depends(get_db)):

    products = db.query(models.Product).filter(
        func.lower(models.Product.company) == company.lower()
    ).all()

    if not products:
        raise HTTPException(status_code=404, detail="Company not found")

    product_ids = [p.id for p in products]

    total_reviews = db.query(models.Review).filter(
        models.Review.product_id.in_(product_ids)
    ).count()

    positive_reviews = db.query(models.Review).filter(
        models.Review.product_id.in_(product_ids),
        models.Review.sentiment == "positive"
    ).count()

    overall_positive_percent = (
        int((positive_reviews / total_reviews) * 100)
        if total_reviews else 0
    )

    model_scores = []

    for p in products:
        pos = db.query(models.Review).filter(
            models.Review.product_id == p.id,
            models.Review.sentiment == "positive"
        ).count()

        total = db.query(models.Review).filter(
            models.Review.product_id == p.id
        ).count()

        score = (pos / total) if total else 0
        model_scores.append((p.model_name, score))

    model_scores.sort(key=lambda x: x[1], reverse=True)

    best_model = model_scores[0][0] if model_scores else None
    worst_model = model_scores[-1][0] if model_scores else None

    return {
        "company": company,
        "total_products": len(products),
        "total_reviews": total_reviews,
        "overall_positive_percent": overall_positive_percent,
        "best_model": best_model,
        "worst_model": worst_model
    }

@router.get("/compare")
def compare_products(model1: str, model2: str, db: Session = Depends(get_db)):

    # 🔎 Find products
    product1 = db.query(models.Product).filter(
        models.Product.model_name.ilike(f"%{model1}%")
    ).first()

    product2 = db.query(models.Product).filter(
        models.Product.model_name.ilike(f"%{model2}%")
    ).first()

    if not product1 or not product2:
        raise HTTPException(status_code=404, detail="One or both products not found")

    def get_stats(product):
        total = db.query(models.Review).filter(
            models.Review.product_id == product.id
        ).count()

        positive = db.query(models.Review).filter(
            models.Review.product_id == product.id,
            models.Review.sentiment == "positive"
        ).count()

        negative = db.query(models.Review).filter(
            models.Review.product_id == product.id,
            models.Review.sentiment == "negative"
        ).count()

        avg_confidence = db.query(func.avg(models.Review.confidence)).filter(
            models.Review.product_id == product.id
        ).scalar() or 0

        return {
            "model_name": product.model_name,
            "company": product.company,
            "current_price": product.current_price,
            "total_reviews": total,
            "positive_percent": int((positive / total) * 100) if total else 0,
            "negative_percent": int((negative / total) * 100) if total else 0,
            "avg_confidence": round(float(avg_confidence), 2)
        }

    stats1 = get_stats(product1)
    stats2 = get_stats(product2)

    # 🏆 Decide better model (based on positive %)
    better_model = (
        stats1["model_name"]
        if stats1["positive_percent"] > stats2["positive_percent"]
        else stats2["model_name"]
    )

    return {
        "comparison": {
            "model1": stats1,
            "model2": stats2,
            "better_model": better_model
        }
    }
    

@router.get("/trend/{brand}")
def brand_trend(brand: str, db: Session = Depends(get_db)):

    reviews = db.query(models.Review).filter(
        func.lower(models.Review.brand) == brand.lower()
    ).order_by(models.Review.id.desc()).all()

    if not reviews:
        return {"message": "No data"}

    # Split latest half vs older half
    mid = len(reviews) // 2

    current_reviews = reviews[:mid]
    previous_reviews = reviews[mid:]

    def calculate_sentiment(data):
        if not data:
            return 0
        positive = sum(1 for r in data if r.sentiment == "positive")
        return int((positive / len(data)) * 100)

    current_percent = calculate_sentiment(current_reviews)
    previous_percent = calculate_sentiment(previous_reviews)

    change = current_percent - previous_percent

    if change > 5:
        trend = "upward"
    elif change < -5:
        trend = "downward"
    else:
        trend = "stable"

    return {
        "brand": brand,
        "current_percent": current_percent,
        "previous_percent": previous_percent,
        "change_percent": change,
        "trend_direction": trend
    }


@router.get("/company-model-insights/{company}")
def company_model_insights(company: str, db: Session = Depends(get_db)):

    products = db.query(models.Product).filter(
        func.lower(models.Product.company) == company.lower()
    ).all()

    response = []

    for product in products:
        total = db.query(models.Review).filter(
            models.Review.product_id == product.id
        ).count()

        positive = db.query(models.Review).filter(
            models.Review.product_id == product.id,
            models.Review.sentiment == "positive"
        ).count()

        negative = db.query(models.Review).filter(
            models.Review.product_id == product.id,
            models.Review.sentiment == "negative"
        ).count()

        response.append({
            "model": product.model_name,
            "total_reviews": total,
            "positive": positive,
            "negative": negative,
            "positive_percent":
                int((positive/total)*100) if total else 0
        })

    return response
=======
>>>>>>> c808026291fc235df6d0142b54f66f2780db5386
