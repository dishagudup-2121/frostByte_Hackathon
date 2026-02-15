from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend import models

router = APIRouter()

@router.get("/brand-summary")
def brand_summary(db: Session = Depends(get_db)):

    result = (
        db.query(
            models.SocialPost.brand,
            func.count(models.SocialPost.id).label("total_posts")
        )
        .group_by(models.SocialPost.brand)
        .all()
    )

    return [
        {
            "brand": r.brand,
            "total_posts": r.total_posts
        }
        for r in result
    ]


@router.get("/location-summary")
def location_summary(db: Session = Depends(get_db)):

    results = (
        db.query(
            models.SocialPost.latitude,
            models.SocialPost.longitude,
            func.count(models.SocialPost.id).label("total_posts")
        )
        .group_by(
            models.SocialPost.latitude,
            models.SocialPost.longitude
        )
        .all()
    )

    return [
        {
            "latitude": r.latitude,
            "longitude": r.longitude,
            "total_posts": r.total_posts
        }
        for r in results
    ]


@router.get("/brand-sentiment-ratio")
def brand_sentiment_ratio(db: Session = Depends(get_db)):

    results = (
        db.query(
            models.SocialPost.brand,
            models.SocialPost.sentiment,
            func.count(models.SocialPost.id).label("count")
        )
        .group_by(
            models.SocialPost.brand,
            models.SocialPost.sentiment
        )
        .all()
    )

    data = {}

    for r in results:
        if r.brand not in data:
            data[r.brand] = {
                "brand": r.brand,
                "positive": 0,
                "negative": 0,
                "neutral": 0
            }

        data[r.brand][r.sentiment] = r.count

    return list(data.values())



@router.get("/product/{id}/reviews")
def get_product_reviews(id: int, sentiment: str = None, db: Session = Depends(get_db)):
    
    query = db.query(models.Review).filter(models.Review.product_id == id)

    if sentiment:
        query = query.filter(models.Review.sentiment == sentiment)

    reviews = query.all()

    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews found")

    return [
        {
            "comment": r.comment,
            "sentiment": r.sentiment,
            "confidence": r.confidence
        }
        for r in reviews
    ]
@router.get("/company-summary/{company}")
def company_summary(company: str, db: Session = Depends(get_db)):

    products = db.query(models.Product).filter(
        func.lower(models.Product.company) == company.lower()
    ).all()

    if not products:
        return {"error": "Company not found"}

    product_ids = [p.id for p in products]

    total_models = len(products)

    total_reviews = db.query(models.Review).filter(
        models.Review.product_id.in_(product_ids)
    ).count()

    positive_reviews = db.query(models.Review).filter(
        models.Review.product_id.in_(product_ids),
        models.Review.sentiment == "positive"
    ).count()

    overall_positive = (
        int((positive_reviews / total_reviews) * 100)
        if total_reviews else 0
    )

    return {
        "company": company,
        "total_models": total_models,
        "total_reviews": total_reviews,
        "overall_positive_percent": overall_positive
    }




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

@router.get("/market-sentiment-share")
def market_sentiment_share(db: Session = Depends(get_db)):

    results = (
        db.query(
            models.Product.company.label("brand"),
            func.count(models.Review.id).label("positive_count")
        )
        .join(models.Review, models.Review.product_id == models.Product.id)
        .filter(func.lower(models.Review.sentiment) == "positive")
        .group_by(models.Product.company)
        .all()
    )

    total_positive = sum(r.positive_count for r in results)

    return [
        {
            "brand": r.brand,
            "sentiment_share": round((r.positive_count / total_positive) * 100, 2)
        }
        for r in results
    ]
@router.get("/feature-comparison")
def feature_comparison(company1: str, company2: str, db: Session = Depends(get_db)):

    features = {
        "price": ["price", "cost", "expensive", "affordable", "value"],
        "comfort": ["comfort", "seat", "interior"],
        "performance": ["performance", "power", "engine", "speed"],
        "mileage": ["mileage", "fuel", "economy"]
    }

    def analyze(company):
        results = {f: 0 for f in features}

        reviews = (
            db.query(models.Review.comment, models.Review.sentiment)
            .join(models.Product, models.Product.id == models.Review.product_id)
            .filter(func.lower(models.Product.company) == company.lower())
            .all()
        )

        for comment, sentiment in reviews:
            if sentiment != "positive":
                continue

            text = comment.lower()
            for f, words in features.items():
                if any(w in text for w in words):
                    results[f] += 1

        total = sum(results.values()) or 1
        return {f: round((v / total) * 100, 1) for f, v in results.items()}

    c1 = analyze(company1)
    c2 = analyze(company2)

    # Get recent reviews for trend (simple version)
    company_reviews = (
    db.query(models.Review)
    .join(models.Product, models.Product.id == models.Review.product_id)
    .filter(func.lower(models.Product.company).in_([company1.lower(), company2.lower()]))
    .order_by(models.Review.id.desc())
    .all()
)

    reviews_c1 = (
    db.query(models.Review)
    .join(models.Product, models.Product.id == models.Review.product_id)
    .filter(func.lower(models.Product.company) == company1.lower())
    .order_by(models.Review.id.desc())
    .all()
)

    reviews_c2 = (
    db.query(models.Review)
    .join(models.Product, models.Product.id == models.Review.product_id)
    .filter(func.lower(models.Product.company) == company2.lower())
    .order_by(models.Review.id.desc())
    .all()
)

    trend = {
    company1: sentiment_trend(reviews_c1),
    company2: sentiment_trend(reviews_c2)
}


# Separate variable for recommendation
    feature_data = {
    company1: c1,
    company2: c2
}

    rec = recommendation(feature_data)

# ⭐ AI insight auto-generation (FIXED)
    insight = []
    for f in c1.keys():
      if c1.get(f, 0) > c2.get(f, 0):
        insight.append(f"{company2} should improve {f}")
      elif c2.get(f, 0) > c1.get(f, 0):
        insight.append(f"{company1} should improve {f}")


    return {
    "company1": company1,
    "company2": company2,
    "features1": c1,
    "features2": c2,
    "ai_insight": " | ".join(insight),
    "trend": trend,
    "recommendation": rec
}


def sentiment_trend(reviews):
    # last 30 vs previous 30
    recent = reviews[:30]
    previous = reviews[30:60]

    def avg(data):
        if not data:
            return 0
        score = sum(
            1 if r.sentiment == "positive"
            else -1 if r.sentiment == "negative"
            else 0
            for r in data
        )
        return score / len(data)

    r1 = avg(recent)
    r2 = avg(previous)

    if r1 > r2:
        return "↑ Improving"
    elif r1 < r2:
        return "↓ Declining"
    else:
        return "→ Stable"

def recommendation(features):
    best_perf = max(features, key=lambda x: features[x]["performance"])
    best_value = max(features, key=lambda x: features[x]["price"])
    best_overall = max(features, key=lambda x: sum(features[x].values()))

    return {
        "Best Performance": best_perf,
        "Best Value": best_value,
        "Best Overall Sentiment": best_overall
    }




