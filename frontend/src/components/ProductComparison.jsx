import React, { useState } from "react";
import { compareProducts } from "../api/productApi";

export default function ProductComparison() {

  const [model1, setModel1] = useState("");
  const [model2, setModel2] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleCompare = async () => {
    if (!model1 || !model2) return;

    try {
      const res = await compareProducts(model1, model2);
      setResult(res.data.comparison);
      setError(null);
    } catch (err) {
      setError("Comparison failed. Check model names.");
      setResult(null);
    }
  };

  return (
    <div className="card glass-card anim-up">
      <h3><span className="text-gradient">Product</span> Comparison</h3>

      <div className="input-group-premium">
        <input
          className="premium-input"
          placeholder="Model 1"
          value={model1}
          onChange={(e) => setModel1(e.target.value)}
        />
        <input
          className="premium-input"
          placeholder="Model 2"
          value={model2}
          onChange={(e) => setModel2(e.target.value)}
        />
        <button className="premium-btn" onClick={handleCompare}>
          Compare
        </button>
      </div>

      {error && <p className="error-text">{error}</p>}

      {result && (
        <div className="insights-grid">
          <div className="insight-box">
            <h4>{result.model1.model_name}</h4>
            <p>Price: ₹{result.model1.current_price}</p>
            <p>Positive: {result.model1.positive_percent}%</p>
            <p>Reviews: {result.model1.total_reviews}</p>
          </div>

          <div className="insight-box">
            <h4>{result.model2.model_name}</h4>
            <p>Price: ₹{result.model2.current_price}</p>
            <p>Positive: {result.model2.positive_percent}%</p>
            <p>Reviews: {result.model2.total_reviews}</p>
          </div>
        </div>
      )}

      {result && (
        <div style={{ marginTop: "20px", textAlign: "center" }}>
          <strong>🏆 Better Model: {result.better_model}</strong>
        </div>
      )}
    </div>
  );
}

