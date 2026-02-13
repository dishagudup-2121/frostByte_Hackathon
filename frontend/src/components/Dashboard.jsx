import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { Bar, Radar } from "react-chartjs-2";
import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import jsPDF from "jspdf";
import html2canvas from "html2canvas";

import ProductDetails from "./ProductDetails";
import ReviewPanels from "./ReviewSummaryCards";
import ProductComparison from "./ProductComparison";
import { getCompanyAnalytics } from "../api/productApi";
import CompanyInsights from "./CompanyInsights";



import "leaflet/dist/leaflet.css";
import "chart.js/auto";
import "../App.css";

const API = "http://127.0.0.1:8000";

export default function Dashboard() {
  const navigate = useNavigate();
  const reportRef = useRef();

  const [text, setText] = useState("");

  // 🔥 Separate states
  const [sentimentResult, setSentimentResult] = useState(null);
  const [productResult, setProductResult] = useState(null);

  const [brandData, setBrandData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);

  const [radarScores, setRadarScores] = useState(new Array(10).fill(25));

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const res = await axios.get(`${API}/analytics/brand-summary`);
      setBrandData(res.data);
    } catch (err) {
      console.error("Sync Error:", err);
    }
  };

  const updateRadar = (data) => {
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

    const topic = (data.key_topic || "other").toLowerCase();
    const index = TOPICS.indexOf(topic);
    const scores = new Array(10).fill(25);

    if (index !== -1) {
      scores[index] =
        data.sentiment === "positive"
          ? 100
          : data.sentiment === "negative"
          ? 15
          : 60;

      setRadarScores(scores);
    }
  };

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
          time: new Date().toLocaleTimeString(),
          markerColor:
            res.data.sentiment === "positive"
              ? "#00f2ff"
              : res.data.sentiment === "negative"
              ? "#ff0055"
              : "#fbff00",
        };

        setSentimentResult(newData);
        setHistory((prev) => [newData, ...prev]);
        updateRadar(res.data);
        fetchAnalytics();
      } catch (err) {
        console.error("Analysis failed:", err);
      } finally {
        setLoading(false);
      }
    });
  };

  const exportPDF = () => {
    const input = reportRef.current;
    html2canvas(input, { scale: 2, useCORS: true }).then((canvas) => {
      const imgData = canvas.toDataURL("image/png");
      const pdf = new jsPDF("p", "mm", "a4");
      pdf.addImage(imgData, "PNG", 0, 0, 210, 297);
      pdf.save("GeoDrive_Command_Report.pdf");
    });
  };

  return (
    <div className="dashboard-root">
      <div className="bg-glow"></div>

      <main className="dashboard-container-v3" ref={reportRef}>
        {/* Header */}
        <header className="header-top anim-up">
          <button
            className="back-home-btn"
            onClick={() => navigate("/")}
          >
            Home
          </button>

          <div className="header-title-group">
            <h1 className="hero-title-small">
              <span className="text-gradient">GeoDrive</span> Pro Dashboard
            </h1>
            <p className="subtitle">Intelligence Hub</p>
          </div>

          <button className="export-btn" onClick={exportPDF}>
            Export PDF
          </button>
        </header>

        {/* Neural Input */}
        <section className="card glass-card anim-up">
          <div className="input-vertical-group">
            <textarea
              placeholder="Enter automotive feedback for neural mapping..."
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
                {loading ? (
                  <span className="loader-small"></span>
                ) : (
                  "Execute Neural Analysis"
                )}
              </button>
            </div>
          </div>
        </section>

        {/* Deep Scan */}
        <div className="product-insight-row">
  <ProductDetails onDataReceived={(d)=>setProductResult(d)} />
  <CompanyInsights company={productResult?.company} />
</div>




        {productResult && productResult.product_id && (
          <section className="card glass-card anim-up">
            <h3>
              Neural Review Comparison:{" "}
              {productResult.model_name || "Deep Scan"}
            </h3>
            <ReviewPanels productId={productResult.product_id} />
          </section>
        )}

        {/* Comparison Section */}
        <ProductComparison />

        {/* Map & Activity */}
        <div className="mid-visual-grid anim-up">
          <div className="card map-card">
            <h3>Sentiment Heatmap</h3>
            <div
              className="map-wrapper"
              style={{
                height: "450px",
                borderRadius: "24px",
                overflow: "hidden",
              }}
            >
              <MapContainer
                center={[18.5204, 73.8567]}
                zoom={8}
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
                      fillOpacity: 0.9,
                      weight: 5,
                    }}
                    radius={14}
                  >
                    <Popup>
                      <div style={{ color: "#000" }}>
                        <strong>{item.brand}</strong>
                        <br />
                        {item.sentiment}
                      </div>
                    </Popup>
                  </CircleMarker>
                ))}
              </MapContainer>
            </div>
          </div>

          <div className="card log-card">
            <h3>Live Activity Feed</h3>
            <div className="history-list">
              {history.length === 0 && (
                <p className="text-muted">
                  Awaiting neural input...
                </p>
              )}

              {history.map((h, i) => (
                <div key={i} className="history-item">
                  <div className="log-header">
                    <span>{h.time}</span>
                    <span className={h.sentiment.toLowerCase()}>
                      {h.sentiment.toUpperCase()}
                    </span>
                  </div>
                  <strong>{h.brand}</strong>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Charts */}
        <div className="bottom-charts-grid anim-up delay-1">
          <div className="card chart-box">
            <h3>Sentiment Fingerprint (Topic Analysis)</h3>
            <div className="chart-inner">
              <Radar
                data={{
                  labels: [
                    "Mileage",
                    "Engine",
                    "Service",
                    "Price",
                    "Comfort",
                    "Performance",
                    "Design",
                    "Safety",
                    "Features",
                    "Other",
                  ],
                  datasets: [
                    {
                      label: "Neural Score",
                      data: radarScores,
                      backgroundColor: "rgba(99,102,241,0.2)",
                      borderColor: "#6366f1",
                      borderWidth: 2,
                    },
                  ],
                }}
                options={{ responsive: true, maintainAspectRatio: false }}
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
