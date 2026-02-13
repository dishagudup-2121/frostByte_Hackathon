import React, { useState, useEffect } from "react";
import { analyzeProduct } from "../api/productApi";
import LoadingSkeleton from "./LoadingSkeleton";
import { Pie, Radar, Line } from "react-chartjs-2";
import "chart.js/auto";

export default function ProductDetails({ onDataReceived }) {
  const [modelInput, setModelInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [typedVerdict, setTypedVerdict] = useState("");

  // 🔥 Typing Animation
  useEffect(() => {
    if (!result?.ai_verdict) return;

    let i = 0;
    setTypedVerdict("");
    const text = result.ai_verdict;

    const interval = setInterval(() => {
      setTypedVerdict((prev) => prev + text[i]);
      i++;
      if (i >= text.length) clearInterval(interval);
    }, 25);

    return () => clearInterval(interval);
  }, [result]);

  const handleAnalyze = async () => {
    if (!modelInput.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await analyzeProduct(modelInput);
      setResult(res.data);
      onDataReceived(res.data);
    } catch (err) {
      if (err.response?.status === 404) {
        setError("Model not found in database.");
      } else {
        setError("Server error. Try again.");
      }
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
        <p className="subtitle">Detailed Model & Market Intelligence</p>

        <div className="input-group-premium">
          <input
            className="premium-input"
            value={modelInput}
            onChange={(e) => setModelInput(e.target.value)}
            placeholder="Type model name (e.g., Tata Nexon)..."
          />
          <button
            className="premium-btn"
            onClick={handleAnalyze}
            disabled={loading}
          >
            {loading ? "Scanning..." : "Deep Scan"}
          </button>
        </div>

        {error && <p className="error-text">{error}</p>}
        {loading && <LoadingSkeleton />}

        {result && !loading && (
          <div className="result-section">

            <h2>{result.model_name}</h2>
            <p className="text-muted">{result.company}</p>

            {/* 💰 PRICE */}
            <div className="price-box">
              <strong>Current Price:</strong>{" "}
              ₹ {result.current_price?.toLocaleString()}
            </div>

            {/* 📊 MINI PIE CHART */}
            <div className="mini-chart">
              <h4>Sentiment Split</h4>
              <Pie
                data={{
                  labels: ["Positive", "Negative"],
                  datasets: [
                    {
                      data: [
                        result.sentiment_summary?.positive_percent,
                        result.sentiment_summary?.negative_percent,
                      ],
                      backgroundColor: ["#22c55e", "#ef4444"],
                    },
                  ],
                }}
              />
            </div>

            {/* 📡 MINI FINGERPRINT RADAR */}
            {result.fingerprint && (
              <div className="mini-chart">
                <h4>Topic Fingerprint</h4>
                <Radar
                  data={{
                    labels: result.fingerprint.map((f) => f.topic),
                    datasets: [
                      {
                        data: result.fingerprint.map((f) => f.strength),
                        backgroundColor: "rgba(99,102,241,0.2)",
                        borderColor: "#6366f1",
                      },
                    ],
                  }}
                  options={{
                    scales: {
                      r: { min: 0, max: 100 },
                    },
                  }}
                />
              </div>
            )}

            {/* 📈 PRICE TREND */}
            {result.price_history && result.price_history.length > 0 && (
              <div className="mini-chart">
                <h4>Price Trend</h4>
                <Line
                  data={{
                    labels: result.price_history.map((p) => p.month),
                    datasets: [
                      {
                        label: "Price",
                        data: result.price_history.map((p) => p.price),
                        borderColor: "#00f2ff",
                        fill: false,
                      },
                    ],
                  }}
                />
              </div>
            )}

            {/* 🧠 AI VERDICT */}
            <div className="verdict-box">
              <h4>AI Market Verdict</h4>
              <p>{typedVerdict}</p>
            </div>

            <p>Total Reviews: {result.total_reviews}</p>

          </div>
        )}
      </div>
    </div>
  );
}
