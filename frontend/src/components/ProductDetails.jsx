import React, { useState } from "react";
import { analyzeProduct } from "../api/productApi";
import LoadingSkeleton from "./LoadingSkeleton";

export default function ProductDetails({ onDataReceived }) {
  const [comment, setComment] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleAnalyze = async () => {
    if (!comment.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const res = await analyzeProduct(comment);
      setResult(res.data);
      onDataReceived(res.data);
    } catch (err) {
      setError("Failed to retrieve deep insights. Check connection.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="product-insight-section">
      <div className="card glass-card anim-up">
        <h3>
          <span className="text-gradient">Deep Dive</span> Engine
        </h3>

        <div className="input-group-premium">
          <input
            className="premium-input"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Type model name..."
          />

          <button
            className="premium-btn"
            onClick={handleAnalyze}
            disabled={loading}
          >
            {loading ? "Igniting..." : "Deep Scan"}
          </button>
        </div>

        {error && <p className="error-text">{error}</p>}
        {loading && <LoadingSkeleton />}

        {result && (
          <div style={{ marginTop: 20 }}>
            <h2>{result.model_name}</h2>
            <p>{result.company}</p>
            <p>₹ {result.current_price}</p>
          </div>
        )}
      </div>
    </div>
  );
}
