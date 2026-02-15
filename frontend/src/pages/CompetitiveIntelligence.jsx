import React, { useEffect, useState } from "react";
import axios from "axios";
import { Doughnut } from "react-chartjs-2";

import "chart.js/auto";

const API = "http://127.0.0.1:8000";

export default function CompetitiveIntelligence() {
  const [brandData, setBrandData] = useState([]);
  const [competitorInsight, setCompetitorInsight] = useState("");
  const [trendDirection, setTrendDirection] = useState("");
  const [sentimentShare, setSentimentShare] = useState([]);
  const [featureData, setFeatureData] = useState(null);
  const [company1, setCompany1] = useState("");
const [company2, setCompany2] = useState("");
const [comparison, setComparison] = useState(null);





  useEffect(() => {
    fetchBrandSummary();
    fetchFeatureComparison();
  }, []);

 


  const fetchBrandSummary = async () => {
    try {
      const res = await axios.get(`${API}/analytics/brand-summary`);
      setBrandData(res.data);
      generateCompetitorInsight(res.data);

    } catch (err) {
      console.error("Brand summary error:", err);
    }
  };
  const fetchMarketShare = async () => {
  const res = await axios.get(
    "http://127.0.0.1:8000/analytics/market-sentiment-share"
  );
  console.log("Market share:", res.data);
  setSentimentShare(res.data);
};

useEffect(() => {
  fetchMarketShare();
}, []);

  const generateCompetitorInsight = (data) => {
  if (!data || data.length < 2) return;

  const sorted = [...data].sort(
    (a, b) => b.total_posts - a.total_posts
  );

  setCompetitorInsight(
    `${sorted[0].brand} currently leads market sentiment, 
     while ${sorted[1].brand} needs improvement in customer perception.`
  );

  setTrendDirection(
    sorted[0].total_posts > sorted[1].total_posts
      ? "Market leader stable"
      : "Competitive shift happening"
  );
};
const fetchFeatureComparison = async () => {
  try {
    const res = await axios.get(
      `${API}/analytics/feature-comparison`,
      { params: { company1: "BMW", company2: "Hyundai" } }
    );

    setFeatureData(res.data);
  } catch (err) {
    console.error("Feature comparison error:", err);
  }
};

const fetchComparison = async () => {
  try {
    const res = await axios.get(
      `${API}/analytics/feature-comparison`,
      { params: { company1, company2 } }
    );

    setComparison(res.data);
  } catch (err) {
    console.error("Comparison error:", err);
  }
};

  const generateColors = (n) =>
  Array.from({ length: n }, (_, i) =>
    `hsl(${(i * 360) / n}, 70%, 55%)`
  );


  return (
    <div className="dashboard-container-v3">
     <h1 className="hero-title-small">
  <span className="text-gradient">Competitive</span> Intelligence
</h1>


  <div className="action-buttons">
  

  <button
    className="back-btn"
    onClick={() => window.location.href = "/dashboard"}
  >
    Back to Dashboard
  </button>
</div>


      {brandData.length > 0 && (
        <div className="card">
         <h3 className="hero-title-small" style={{ fontSize: "1.6rem" }}>
  <span className="text-gradient">Market</span> Sentiment Share
</h3>


<div style={{ height: "320px", maxWidth: "420px", margin: "auto" }}>
  <Doughnut
    data={{
      labels: sentimentShare.map(b => b.brand || "Unknown"),

      datasets: [{
       data: sentimentShare.map(b => b.sentiment_share || 0),

  backgroundColor: generateColors(sentimentShare.length),
              hoverOffset: 15,

      }],
    }}
           options={{
            cutout: "50%",               // thicker ring (3D feel)
            maintainAspectRatio: false,
            plugins: {
            legend: { position: "bottom" }
               },
            elements: {
            arc: {
      borderWidth: 4,
      borderColor: "#0f172a"   // dark edge for depth
    }
  }
}}

  />

</div>
          {/* Competitor Gap Insight */}
<div className="card" style={{ marginTop: "20px" }}>
  <h3 className="hero-title-small" style={{ fontSize: "1.2rem" }}>
  <span className="text-gradient">Competitor</span> Gap Insight
</h3>
  <p>{competitorInsight}</p>
</div>

{/* Trend Direction */}
<div className="card">
  
  <h3 className="hero-title-small" style={{ fontSize: "1.2rem" }}>

  <span className="text-gradient">Trend</span> Direction

</h3>

  <p>{trendDirection}</p>
</div>

  {/* {featureData && (
  <div className="card">
     <h3 className="hero-title-small" style={{ fontSize: "1.2rem" }}>
  <span className="text-gradient">Feature Level</span> Comparison
</h3>
  

    {Object.keys(featureData?.features1 || {}).map(f => (
      <p key={f}>
        <b>{f.toUpperCase()}</b> :
        {featureData.company1} → {featureData.features1[f]}%
        {" | "}
        {featureData.company2} → {featureData.features2[f]}%
      </p>
    ))}
  </div>
)} */
}


<div className="comparison-card">
  <h2 className="hero-title-small" style={{ fontSize: "1.5rem" }}>

  <span className="text-gradient">Product</span>  Comparison

</h2>

  <div className="compare-inputs">
    <input
      placeholder="Model 1"
      value={company1}
      onChange={(e) => setCompany1(e.target.value)}
    />

    <input
      placeholder="Model 2"
      value={company2}
      onChange={(e) => setCompany2(e.target.value)}
    />

    <button className="compare-btn" onClick={fetchComparison}>
      Compare
    </button>
  </div>
</div>


{comparison?.features1 && comparison?.features2 && (
  <div className="card">
       <h3 className="hero-title-small" style={{ fontSize: "1.5rem" }}>
  <span className="text-gradient">Feature Level</span> Comparison
</h3>

    {Object.keys(comparison.features1).map(f => (
      <p key={f}>
        <b>{f.toUpperCase()}</b> :
        {comparison.company1} → {comparison.features1[f]}% |
        {comparison.company2} → {comparison.features2[f]}%
      </p>
    ))}

    
    <h4 className="hero-title-small" style={{ fontSize: "1.2rem" }}>
  <span className="text-gradient">AI </span> Insights:
</h4>
    
    <p>{comparison?.ai_insight || "No insight available"}</p>

       <h4 className="hero-title-small" style={{ fontSize: "1.2rem" }}>
  <span className="text-gradient">Trend</span> Direction:
</h4>
    <p>
      {comparison?.trend?.[comparison.company1]} |
      {comparison?.trend?.[comparison.company2]}
    </p>

    
      <h4 className="hero-title-small" style={{ fontSize: "1.2rem" }}>
  <span className="text-gradient">Recommendation </span> for you:
</h4>
    
    <p>Best Performance → {comparison?.recommendation?.["Best Performance"]}</p>
    <p>Best Value → {comparison?.recommendation?.["Best Value"]}</p>
    <p>Best Overall → {comparison?.recommendation?.["Best Overall Sentiment"]}</p>
  </div>
)}

        </div>
      )}
    </div>
  );
}




