import React, { useState, useEffect } from "react";
import { getProductReviews } from "../api/productApi";

export default function ReviewPanels({ productId }) {
  const [reviews, setReviews] = useState({ positive: [], negative: [] });
  const [expanded, setExpanded] = useState(null);

  useEffect(() => {
    if (productId) fetchAllReviews();
  }, [productId]);

  const fetchAllReviews = async () => {
    const pos = await getProductReviews(productId, "positive");
    const neg = await getProductReviews(productId, "negative");
    setReviews({ positive: pos.data, negative: neg.data });
  };

  const ReviewCard = ({ review, type, index }) => (
    <div 
      className={`review-card ${type} ${expanded === `${type}-${index}` ? 'expanded' : ''}`}
      onClick={() => setExpanded(expanded === `${type}-${index}` ? null : `${type}-${index}`)}
    >
      <div className="review-badge">{type.toUpperCase()}</div>
      <p className="review-text">{review.text}</p>
      {expanded === `${type}-${index}` && (
        <div className="review-details anim-up">
          <hr />
          <p>Confidence: {(review.confidence * 100).toFixed(1)}%</p>
          <p>Source: {review.source || "Neural Stream"}</p>
        </div>
      )}
    </div>
  );

  return (
    <div className="review-comparison-layout anim-up">
      <div className="review-column">
        <h4>Positive Signals</h4>
        {reviews.positive.map((r, i) => <ReviewCard key={i} review={r} type="positive" index={i} />)}
      </div>
      <div className="review-column">
        <h4>Critical Redlines</h4>
        {reviews.negative.map((r, i) => <ReviewCard key={i} review={r} type="negative" index={i} />)}
      </div>
    </div>
  );
}