import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { Bar, Radar } from "react-chartjs-2";
import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import jsPDF from "jspdf";
import html2canvas from "html2canvas";

import ProductDetails from "./ProductDetails";
import ProductComparison from "./ProductComparison";

import "leaflet/dist/leaflet.css";
import "chart.js/auto";
import "../App.css";

const API = "http://127.0.0.1:8000";

export default function Dashboard() {
  const navigate = useNavigate();
  const reportRef = useRef();

  const [text, setText] = useState("");
  const [productResult, setProductResult] = useState(null);
  const [brandData, setBrandData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);

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
    BMW: "#00f2ff",
    Tata: "#ff0055",
    Hyundai: "#fbff00",
    Mahindra: "#8b5cf6",
    Toyota: "#22c55e",
    Honda: "#ef4444",
  };

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
  const exportPDF = () => {
    const input = reportRef.current;
    html2canvas(input, { scale: 2, useCORS: true }).then((canvas) => {
      const imgData = canvas.toDataURL("image/png");
      const pdf = new jsPDF("p", "mm", "a4");
      pdf.addImage(imgData, "PNG", 0, 0, 210, 297);
      pdf.save("GeoDrive_Report.pdf");
    });
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

          <button className="export-btn" onClick={exportPDF}>
            Export PDF
          </button>
        </header>

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
        <ProductDetails onDataReceived={(data) => setProductResult(data)} />

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
            <div className="chart-inner">
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
                  scales: {
                    r: {
                      min: 0,
                      max: 100,
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
