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



  useEffect(() => {
    fetchBrandSummary();
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


  const generateColors = (n) =>
  Array.from({ length: n }, (_, i) =>
    `hsl(${(i * 360) / n}, 70%, 55%)`
  );


  return (
    <div className="dashboard-container-v3">
      <h1>Competitive Intelligence</h1>

      {brandData.length > 0 && (
        <div className="card">
          <h3>Market Sentiment Share</h3>

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
  <h3>Competitor Gap Insight</h3>
  <p>{competitorInsight}</p>
</div>

{/* Trend Direction */}
<div className="card">
  <h3>Trend Direction</h3>
  <p>{trendDirection}</p>
</div>



        </div>
      )}
    </div>
  );
}





// export default function CompetitiveIntelligence({
//   productA,
//   productB
// }) 
// {

//   const navigate = useNavigate();

//   const exportPDF = () => {
//     const pdf = new jsPDF();
//     let y = 20;

//     pdf.setFontSize(18);
//     pdf.text("Competitive Intelligence Report", 20, y);

//     y += 15;

//     pdf.setFontSize(12);
//     pdf.text(`Product A: ${productA?.model_name}`, 20, y);
//     y += 8;
//     pdf.text(`Product B: ${productB?.model_name}`, 20, y);

//     y += 12;
//     pdf.text("Market Sentiment Share:", 20, y);
//     y += 8;
//     pdf.text(
//       `${productA?.model_name}: ${productA?.positive_percent}%`,
//       20,
//       y
//     );
//     y += 8;
//     pdf.text(
//       `${productB?.model_name}: ${productB?.positive_percent}%`,
//       20,
//       y
//     );

//     pdf.save("Competitive_Report.pdf");
//   };

//   const competitorGapInsight = () => {
//     if (!productA || !productB) return "";

//     if (productA.positive_percent > productB.positive_percent)
//       return `${productA.model_name} has stronger market sentiment advantage.`;

//     return `${productB.model_name} currently leads customer perception.`;
//   };

//   return (
//     <div className="comp-intel-page">

//       {/* HEADER */}
//       <div className="comp-header">
//         <button
//           className="comp-btn back-btn"
//           onClick={() => navigate("/dashboard")}
//         >
//           ← Back Dashboard
//         </button>

//         <button
//           className="comp-btn"
//           onClick={exportPDF}
//         >
//           Export Report
//         </button>
//       </div>

//       {/* SENTIMENT SHARE */}
//       <div className="comp-card">
//         <div className="comp-title">
//           Market Sentiment Share
//         </div>

//         <p>{productA?.model_name}: {productA?.positive_percent}%</p>
//         <p>{productB?.model_name}: {productB?.positive_percent}%</p>
//       </div>

//       {/* PRICE INSIGHT */}
//       <div className="comp-card">
//         <div className="comp-title">
//           Price Perception Insight
//         </div>

//         <p>
//           {productA?.current_price > productB?.current_price
//             ? `${productA.model_name} positioned premium.`
//             : `${productB.model_name} positioned premium.`}
//         </p>
//       </div>

//       {/* COMPETITOR GAP */}
//       <div className="comp-card">
//         <div className="comp-title">
//           Competitor Gap Insight
//         </div>

//         <p>{competitorGapInsight()}</p>
//       </div>

//       {/* TREND INSIGHT */}
//       <div className="comp-card">
//         <div className="comp-title">
//           Trend Direction
//         </div>

//         <p>
//           Hyundai sentiment ↑ last month, BMW slightly ↓
//           (Example AI trend insight placeholder).
//         </p>
//       </div>

//     </div>
//   );
// }
