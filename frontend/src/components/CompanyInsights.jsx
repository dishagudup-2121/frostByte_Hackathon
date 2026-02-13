import React, { useState } from "react";
import axios from "axios";
import { Bar, Pie } from "react-chartjs-2";
import "chart.js/auto";

const API = "http://127.0.0.1:8000";

export default function CompanyInsights({ company }) {
  const [models, setModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState(null);
  const [loading, setLoading] = useState(false);

  // 🔥 Fetch company model insights
  const fetchCompanyData = async () => {
    if (!company) return;

    setLoading(true);
    try {
      const res = await axios.get(
        `${API}/analytics/company-model-insights/${company}`
      );
      setModels(res.data);
    } catch (err) {
      console.error("Company insights error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card company-insights">

      <h3 className="text-gradient">Company Insights</h3>

      <button className="premium-btn" onClick={fetchCompanyData}>
        {loading ? "Loading..." : "View Insights"}
      </button>

      {/* MODEL LIST */}
      {models.length > 0 && (
        <div className="model-list">
          <h4>Top Models</h4>

          {models.map((m, i) => (
            <div
              key={i}
              className="history-item"
              onClick={() => setSelectedModel(m)}
              style={{ cursor: "pointer" }}
            >
              <strong>{m.model}</strong>
              <br />
              Reviews: {m.total_reviews}
            </div>
          ))}
        </div>
      )}

      {/* BAR CHART → Selected Model */}
      {selectedModel && (
        <div className="chart-section">
          <h4>{selectedModel.model} Review Sentiment</h4>

          <Bar
            data={{
              labels: ["Positive", "Negative"],
              datasets: [
                {
                  data: [
                    selectedModel.positive,
                    selectedModel.negative,
                  ],
                  backgroundColor: ["#22c55e", "#ef4444"],
                },
              ],
            }}
          />
        </div>
      )}

      {/* PIE CHART → Positive % per Model */}
      {models.length > 0 && (
        <div className="chart-section">
          <h4>Positive Reviews Share</h4>

          <Pie
            data={{
              labels: models.map((m) => m.model),
              datasets: [
                {
                  data: models.map((m) => m.positive_percent),
                  backgroundColor: [
                    "#6366f1",
                    "#22c55e",
                    "#f97316",
                    "#ec4899",
                    "#00f2ff",
                    "#8b5cf6",
                  ],
                },
              ],
            }}
          />
        </div>
      )}

    </div>
  );
}
