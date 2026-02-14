import React, { useState, useEffect } from "react";
import axios from "axios";
import { Pie } from "react-chartjs-2";
import "chart.js/auto";

const API = "http://127.0.0.1:8000";

export default function CompanyInsights({ company }) {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchCompanyData = async () => {
    if (!company) return;

    setLoading(true);
    try {
      const res = await axios.get(
        `${API}/company/brand-models/${company}`
      );
      setModels(res.data);
    } catch (err) {
      console.error("Company insights error:", err);
    } finally {
      setLoading(false);
    }
  };

  // AUTO LOAD when deep scan selects company
  useEffect(() => {
    fetchCompanyData();
  }, [company]);

  return (
    <div className="card company-insights">

      <h3 className="text-gradient">Company Insights</h3>

      {/* BUTTON */}
      <button
        className="premium-btn"
        onClick={fetchCompanyData}
      >
        {loading ? "Loading..." : "View Company Insights"}
      </button>

      {/* MODEL LIST */}
      {models.length > 0 && (
        <div className="model-list">
          <h4>Top Models</h4>

          {models?.length > 0 &&
  models.map((m, i) => (
    <div key={m.id || i} className="history-item">
      <strong>{m.model || m.model_name}</strong>
      <br />
      Reviews: {m.total_reviews || 0}
    </div>
  ))}

        </div>
      )}

      {/* PIE CHART */}
      {models.length > 0 && (
        <div className="chart-section">
          <h4>Positive Review Share</h4>

          <Pie
            data={{
              labels: models.map(m => m.model),
              datasets: [{
                data: models.map(m => m.positive_percent),
                backgroundColor: [
                  "#6366f1",
                  "#22c55e",
                  "#f97316",
                  "#ec4899",
                  "#00f2ff",
                  "#8b5cf6",
                ],
              }],
            }}
          />
        </div>
      )}

    </div>
  );
}
