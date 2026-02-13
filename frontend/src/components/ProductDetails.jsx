import React, { useState } from "react";
import { analyzeProduct } from "../api/productApi";
import LoadingSkeleton from "./LoadingSkeleton";

export default function ProductDetails({ onDataReceived }) {
  const [comment, setComment] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalyze = async () => {
    if (!comment.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await analyzeProduct(comment);
      onDataReceived(res.data);
      {result?.model_name && (
  <div>
    <h2>{result.model_name}</h2>
    <p>{result.company}</p>
    <p>₹ {result.current_price}</p>
  </div>
)}

    } catch (err) {
      setError("Failed to retrieve deep insights. Check connection.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="product-insight-section">
      <div className="card glass-card anim-up">
        <h3><span className="text-gradient">Deep Dive</span> Engine</h3>
        <p className="subtitle">Detailed Model & Price Analysis</p>
        
        <div className="input-group-premium">
          <input
            className="premium-input"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Type model name (e.g., Porsche 911 Turbo)..."
          />
          <button className="premium-btn" onClick={handleAnalyze} disabled={loading}>
            {loading ? "Igniting..." : "Deep Scan"}
          </button>
        </div>

        {error && <p className="error-text">{error}</p>}
        {loading && <LoadingSkeleton />}
      </div>
    </div>
  );
}