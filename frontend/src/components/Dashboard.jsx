import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { Bar, Radar } from "react-chartjs-2";
import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import jsPDF from "jspdf";
import html2canvas from "html2canvas";

import ProductDetails from "./ProductDetails";
import ProductComparison from "./ProductComparison";
import { getCompanyAnalytics } from "../api/productApi";
import CompanyInsights from "./CompanyInsights";



import "leaflet/dist/leaflet.css";
import "chart.js/auto";
import "../App.css";

import { getBrandTrend } from "../api/trendApi";


const API = "http://127.0.0.1:8000";

export default function Dashboard() {
  const navigate = useNavigate();
  const reportRef = useRef();
  const radarRef = useRef(null);


  const [text, setText] = useState("");
  const [productResult, setProductResult] = useState(null);
  const [brandData, setBrandData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [exportType, setExportType] = useState("product");
  const [brandTrend, setBrandTrend] = useState(null);


  const TOPICS = [
    "mileage",
    "engine",
    "service",
    "price",
    "comfort",
    "performance",
    "design",
    "safety",
    "features",
    "other",
  ];

  const [radarScores, setRadarScores] = useState(new Array(10).fill(0));

  // 🔥 Brand Colors
  const brandColors = {
    BMW: "#116569",
    Tata: "#e11a5c",
    Hyundai: "#d5d818",
    Mahindra: "#814ff5",
    Toyota: "#20b858",
    Honda: "#f55c5c",
  };

  useEffect(() => {
  if (productResult?.company) {
    getBrandTrend(productResult.company.toLowerCase()).then(data => {
      console.log("Trend API Response:", data);
      setBrandTrend(data);
    });
  }
}, [productResult]);


  // ==========================================================
  // Load initial analytics + map history
  // ==========================================================
  useEffect(() => {
    fetchAnalytics();
    fetchMapHistory();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const res = await axios.get(`${API}/analytics/brand-summary`);
      setBrandData(res.data);
    } catch (err) {
      console.error("Analytics Error:", err);
    }
  };

  const fetchMapHistory = async () => {
    try {
      const res = await axios.get(`${API}/posts`);
      const formatted = res.data.map((item) => ({
        ...item,
        lat: item.latitude,
        lng: item.longitude,
        markerColor: brandColors[item.brand] || "#ffffff",
      }));
      setHistory(formatted);
    } catch (err) {
      console.error("Map Load Error:", err);
    }
  };

  // ==========================================================
  // 🔥 NEW Intelligent Radar Logic (Fingerprint Based)
  // ==========================================================
  useEffect(() => {
    if (productResult?.fingerprint?.length > 0) {
      const scores = new Array(TOPICS.length).fill(0);

      productResult.fingerprint.forEach((item) => {
        const index = TOPICS.indexOf(item.topic.toLowerCase());
        if (index !== -1) {
          scores[index] = item.strength;
        }
      });

      setRadarScores(scores);
    } else {
      setRadarScores(new Array(TOPICS.length).fill(0));
    }
  }, [productResult]);

  // ==========================================================
  // Analyze Sentiment
  // ==========================================================
  const analyze = async () => {
    if (!text.trim()) return;
    setLoading(true);

    navigator.geolocation.getCurrentPosition(async (pos) => {
      try {
        const res = await axios.post(`${API}/ai/analyze`, {
          text,
          latitude: pos.coords.latitude,
          longitude: pos.coords.longitude,
        });

        const newData = {
          ...res.data,
          lat: pos.coords.latitude,
          lng: pos.coords.longitude,
          markerColor: brandColors[res.data.brand] || "#ffffff",
          time: new Date().toLocaleTimeString(),
        };

        setHistory((prev) => [newData, ...prev]);
        fetchAnalytics();
        setText("");
      } catch (err) {
        console.error("Analysis failed:", err);
      } finally {
        setLoading(false);
      }
    });
  };

  // ==========================================================
  // Export PDF
  // ==========================================================


  const exportPDF = async (type) => {
    const pdf = new jsPDF("p", "mm", "a4");
    const pageWidth = pdf.internal.pageSize.getWidth();
    let y = 20;

    // HEADER
    pdf.setFillColor(99, 102, 241);
    pdf.rect(0, 0, pageWidth, 25, "F");

    pdf.setFontSize(18);
    pdf.setTextColor(255, 255, 255);
    pdf.text("GeoDrive Intelligence Report", pageWidth / 2, 15, { align: "center" });

    pdf.setTextColor(0);
    y = 40;

    // ==============================
    // 🟢 PRODUCT REPORT
    // ==============================
    if (type === "product" && productResult) {

      pdf.setFontSize(16);
      pdf.text("Executive Summary", 15, y);
      y += 10;

      pdf.setFontSize(11);
      pdf.text(
        `${productResult.model_name} shows ${
          productResult.sentiment_summary?.positive_percent || 0
        }% positive sentiment from ${
          productResult.total_reviews || 0
        } reviews.`,
        15,
        y,
        { maxWidth: 180 }
      );

    }

    // ==============================
    // 🔵 COMPANY REPORT
    // ==============================
    if (type === "company" && productResult?.company) {

      pdf.setFontSize(16);
      pdf.text("Company Intelligence Summary", 15, y);
      y += 10;

      pdf.setFontSize(11);
      pdf.text(
        `Company: ${productResult.company}`,
        15,
        y
      );
      y += 8;

      pdf.text(
        `Total Reviews: ${productResult.total_reviews || 0}`,
        15,
        y
      );
    }

    // ==============================
    // 🟣 FULL REPORT
    // ==============================
    if (type === "full") {

      pdf.setFontSize(16);
      pdf.text("Full Intelligence Snapshot", 15, y);
      y += 10;

      pdf.setFontSize(11);
      pdf.text(
        "This report includes full dashboard analytics, brand volume, product sentiment and intelligence insights.",
        15,
        y,
        { maxWidth: 180 }
      );

    }

    pdf.line(15, y, 195, y);
    y += 5; 

    if (y > 260) {
      pdf.addPage();
      y = 20;
    }

    // Footer
    pdf.setFontSize(9);
    pdf.setTextColor(120);
    pdf.text(
      "Generated by GeoDrive AI – FrostByte Hackathon 2026",
      pageWidth / 2,
      285,
      { align: "center" }
    );

    pdf.save("GeoDrive_Report.pdf");
  };

  return (
    <div className="dashboard-root">
      <div className="bg-glow"></div>

      <main className="dashboard-container-v3" ref={reportRef}>
        {/* Header */}
<header className="header-top anim-up">
  <button className="back-home-btn" onClick={() => navigate("/")}>
    Home
  </button>

  <div>
    <h1 className="hero-title-small">
      <span className="text-gradient">GeoDrive</span> Pro Dashboard
    </h1>
    <p className="subtitle">Intelligence Hub</p>
  </div>

  <div className="header-actions">
    <button className="export-btn" onClick={exportPDF}>
      Export PDF
    </button>

    <button
      className="comp-nav-btn"
      onClick={() => navigate("/competitive")}
    >
      Competitive Intelligence
    </button>
    <button
      className="team-btn"
      onClick={() => navigate("/team")}
    >
      Team Info
    </button>
    {/* <button onClick={() => window.location.href="/team"}>
  Team Info
</button> */}

  </div>
</header>

<<<<<<< HEAD
          <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
            <select
              value={exportType}
              onChange={(e) => setExportType(e.target.value)}
              style={{
                padding: "8px 12px",
                borderRadius: "8px",
                background: "#0f172a",
                color: "white",
                border: "1px solid #334155"
              }}
            >
              <option value="product">Product Report</option>
              <option value="company">Company Report</option>
              <option value="full">Full Intelligence</option>
            </select>

            <button
              className="export-btn"
              onClick={() => exportPDF(exportType)}
            >
              Export
            </button>
          </div>


        </header>
=======
>>>>>>> c808026291fc235df6d0142b54f66f2780db5386

        {/* Input Section */}
        <section className="card glass-card anim-up">
          <textarea
            placeholder="Enter automotive feedback..."
            value={text}
            onChange={(e) => setText(e.target.value)}
            className="premium-textarea"
          />

          <div className="btn-center-wrap">
            <button
              onClick={analyze}
              className="premium-btn"
              disabled={loading}
            >
              {loading ? "Processing..." : "Execute Neural Analysis"}
            </button>
          </div>
        </section>

        {/* Deep Scan */}
        <div className="product-insight-row">
<<<<<<< HEAD
          <ProductDetails onDataReceived={(d)=>setProductResult(d)} />
          <CompanyInsights company={productResult?.company} />
        </div>
=======
          
  <ProductDetails onDataReceived={(d)=>setProductResult(d)} />

  <CompanyInsights company={productResult?.company} />
</div>
>>>>>>> c808026291fc235df6d0142b54f66f2780db5386

        {brandTrend && (
          <div className="card">
            <h3>Market Trend Insight</h3>

            <p>
              Current 30 Days: {brandTrend.current_percent}%
            </p>

            <p>
              Previous 30 Days: {brandTrend.previous_percent}%
            </p>

            <p>
              Change: {brandTrend.change_percent > 0 ? "+" : ""}
              {brandTrend.change_percent}%
            </p>

            <p>
              Trend Direction:{" "}
              {brandTrend.trend_direction === "upward"
                ? "📈 Improving"
                : brandTrend.trend_direction === "downward"
                ? "📉 Declining"
                : "➡ Stable"}
            </p>
          </div>
        )}

        <button
          className="trend-btn"
          onClick={() => {
            console.log("Brand:", productResult?.brand);
            getBrandTrend(productResult?.company?.toLowerCase()).then(data => {
              console.log("Trend Data:", data);
              setBrandTrend(data);
            });
          }}
        >
          Show Market Trend
        </button>



        <ProductComparison />

        {/* Map + Activity */}
        <div className="mid-visual-grid anim-up">
          <div className="card map-card">
            <h3>Brand Sentiment Map</h3>
            <div style={{ height: "450px", borderRadius: "24px", overflow: "hidden" }}>
              <MapContainer
                center={[20.5937, 78.9629]}
                zoom={5}
                style={{ height: "100%", width: "100%" }}
              >
                <TileLayer url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" />

                {history.map((item, i) => (
                  <CircleMarker
                    key={i}
                    center={[item.lat, item.lng]}
                    pathOptions={{
                      color: item.markerColor,
                      fillColor: item.markerColor,
                      fillOpacity: 0.8,
                    }}
                    radius={8}
                  >
                    <Popup>
                      <strong>{item.brand}</strong>
                      <br />
                      {item.sentiment}
                    </Popup>
                  </CircleMarker>
                ))}
              </MapContainer>
            </div>
          </div>

          {/* Live Feed */}
          <div className="card log-card">
            <h3>Live Activity Feed</h3>
            <div className="history-list">
              {history.map((h, i) => (
                <div key={i} className="history-item">
                  <div className="log-header">
                    <span>{h.time || "Stored"}</span>
                    <span className={h.sentiment?.toLowerCase()}>
                      {h.sentiment?.toUpperCase()}
                    </span>
                  </div>
                  <strong>{h.brand}</strong>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Charts */}
        <div className="bottom-charts-grid">
          <div className="card chart-box">
            <h3>Sentiment Fingerprint</h3>
            <div className="chart-inner" ref={radarRef} style={{height: "300px", background: "#1c3d5400", padding: "20px", borderRadius: "12px" }}>
              <Radar
                data={{
                  labels: TOPICS.map(
                    (t) => t.charAt(0).toUpperCase() + t.slice(1)
                  ),
                  datasets: [
                    {
                      label: "Topic Strength (%)",
                      data: radarScores,
                      backgroundColor: "rgba(99,102,241,0.2)",
                      borderColor: "#6366f1",
                      borderWidth: 2,
                    },
                  ],
                }}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      labels: {
                        color: "#ffffff",
                        font: {
                          size: 13,
                          weight: "600",
                        },
                      },
                    },
                  },
                  scales: {
                    r: {
                      min: 0,
                      max: 100,
                      ticks: {
                        stepSize: 20,
                        display:false,
                        color: "#94a3b8",
                        backdropColor: "transparent", // ❌ removes grey boxes
                        font: {
                          size: 11,
                          weight: "500",
                        },
                      },
                      grid: {
                        color: "rgba(255,255,255,0.08)",
                      },
                      angleLines: {
                        color: "rgba(255,255,255,0.1)",
                      },
                      pointLabels: {
                        color: "#e2e8f0",
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

          <div className="card chart-box">
            <h3>Market Brand Volume</h3>
            <div className="chart-inner">
              <Bar
                data={{
                  labels: brandData.map((b) => b.brand),
                  datasets: [
                    {
                      label: "Total Mentions",
                      data: brandData.map((b) => b.total_posts),
                      backgroundColor: "#6366f1",
                      borderRadius: 8,
                    },
                  ],
                }}
                options={{ responsive: true, maintainAspectRatio: false }}
              />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
} 