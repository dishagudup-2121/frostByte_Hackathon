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

  // Typing animation
  useEffect(() => {
    if (!result?.ai_verdict) return;

    let index = 0;
    setTypedVerdict("");
    const fullText = result.ai_verdict;

    const interval = setInterval(() => {
      setTypedVerdict(fullText.slice(0, index + 1));
      index++;

      if (index >= fullText.length) {
        clearInterval(interval);
      }
    }, 20);

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

        {/* INPUT */}
        <div className="input-group-premium">
          <input
            className="premium-input"
            value={modelInput}
            onChange={(e) => setModelInput(e.target.value)}
            placeholder="Type model name (e.g., BMW X5)..."
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

        {/* ================= RESULT ================= */}
        {result && !loading && (
          <div className="result-section">

            <h2>{result.model_name}</h2>
            <p className="text-muted">{result.company}</p>

            <div className="price-box">
              <strong>Current Price:</strong> ₹{" "}
              {result.current_price?.toLocaleString()}
            </div>

            {/* ================= CHARTS ================= */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "40px",
                marginTop: "40px",
                alignItems: "start"
              }}
            >

              {/* PIE */}
              <div style={{ minHeight: "280px" }}>
                <h4>Sentiment Split</h4>
                <div style={{ height: "250px" }}>
                  <Pie
                    data={{
                      labels: ["Positive", "Negative"],
                      datasets: [
                        {
                          data: [
                            result.sentiment_summary?.positive_percent || 0,
                            result.sentiment_summary?.negative_percent || 0,
                          ],
                          backgroundColor: ["#22c55e", "#ef4444"],
                        },
                      ],
                    }}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                    }}
                  />
                </div>
              </div>

             {/* RADAR */}
              <div style={{ minHeight: "320px" }}>
                <h4 style={{ marginBottom: "15px" }}>Topic Fingerprint</h4>

                <div style={{ height: "280px" }}>
                  <Radar
                    data={{
                      labels: result.fingerprint?.map((f) =>
                        f.topic.charAt(0).toUpperCase() + f.topic.slice(1)
                      ) || [],
                      datasets: [
                        {
                          label: "Strength %",
                          data:
                            result.fingerprint?.map((f) => f.strength) || [],
                          backgroundColor: "rgba(99,102,241,0.15)",
                          borderColor: "#6366f1",
                          borderWidth: 2,
                          pointBackgroundColor: "#00f2ff",
                          pointBorderColor: "#ffffff",
                          pointRadius: 4,
                          pointHoverRadius: 6,
                        },
                      ],
                    }}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: {
                          display: false,
                        },
                      },
                      scales: {
                        r: {
                          min: 0,
                          max: 100,
                          ticks: {
                            stepSize: 20,
                            backdropColor: "transparent",
                            color: "#94a3b8",
                            font: {
                              size: 11,
                            },
                          },
                          grid: {
                            color: "rgba(255,255,255,0.08)",
                          },
                          angleLines: {
                            color: "rgba(255,255,255,0.08)",
                          },
                          pointLabels: {
                            color: "#ffffff",
                            font: {
                              size: 13,
                              weight: "600",
                            },
                          },
                        },
                      },
                    }}
                  />
                </div>
              </div>

            </div>

            {/* ================= PRICE TREND ================= */}
            {result.price_history?.length > 0 && (
              <div style={{ marginTop: "50px" }}>
                <h4>Price Trend</h4>
                <div style={{ height: "260px" }}>
                  <Line
                    data={{
                      labels: result.price_history.map((p) => p.month),
                      datasets: [
                        {
                          label: "Price",
                          data: result.price_history.map((p) => p.price),
                          borderColor: "#00f2ff",
                          tension: 0.3,
                          fill: false,
                        },
                      ],
                    }}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                    }}
                  />
                </div>
              </div>
            )}

            {/* ================= VERDICT ================= */}
            <div
              className="verdict-box"
              style={{
                marginTop: "50px",
                padding: "25px",
                position: "relative",
                zIndex: 2
              }}
            >
              <h4>AI Market Verdict</h4>
              <p style={{ lineHeight: "1.6" }}>{typedVerdict}</p>
            </div>

            <p style={{ marginTop: "20px" }}>
              Total Reviews: {result.total_reviews}
            </p>

          </div>
        )}
      </div>
    </div>
  );
}
