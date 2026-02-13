import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { Bar, Radar } from "react-chartjs-2";
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import jsPDF from "jspdf";
import html2canvas from "html2canvas";
import "leaflet/dist/leaflet.css";
import "chart.js/auto";
import "../App.css";

const API = "http://127.0.0.1:8000";

export default function Dashboard() {
  const navigate = useNavigate();
  const reportRef = useRef(); 
  
  // --- State Management ---
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [brandData, setBrandData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]); 
  const [radarScores, setRadarScores] = useState([30, 30, 30, 30, 30, 30, 30, 30, 30, 30]);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const res = await axios.get(`${API}/analytics/brand-summary`);
      setBrandData(res.data);
    } catch (err) { console.error("Database fetch failed:", err); }
  };

  const updateRadar = (data) => {
    const TOPICS = ['mileage', 'engine', 'service', 'price', 'comfort', 'performance', 'design', 'safety', 'features', 'other'];
    const topic = data.key_topic.toLowerCase();
    const index = TOPICS.indexOf(topic);
    
    // Reset to a low baseline (30) so the spike (100) is visually dramatic
    const newScores = [30, 30, 30, 30, 30, 30, 30, 30, 30, 30]; 
    if (index !== -1) {
      newScores[index] = data.sentiment === "positive" ? 100 : data.sentiment === "negative" ? 20 : 65;
      setRadarScores(newScores);
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
          markerColor: res.data.sentiment === 'positive' ? '#00f2ff' : 
                       res.data.sentiment === 'negative' ? '#ff0055' : '#fbff00'
        };

        setResult(newData);
        setHistory(prev => [newData, ...prev]); 
        updateRadar(res.data);
        fetchAnalytics();
      } catch (err) { console.error("Neural analysis failed:", err); }
      finally { setLoading(false); }
    });
  };

  const exportPDF = () => {
    const input = reportRef.current;
    html2canvas(input, { scale: 2, useCORS: true }).then((canvas) => {
      const imgData = canvas.toDataURL("image/png");
      const pdf = new jsPDF("p", "mm", "a4");
      pdf.addImage(imgData, "PNG", 0, 0, 210, 297);
      pdf.save(`GeoDrive_Insight_Report.pdf`);
    });
  };

  const radarData = {
    labels: ['Mileage', 'Engine', 'Service', 'Price', 'Comfort', 'Performance', 'Design', 'Safety', 'Features', 'Other'],
    datasets: [{
      label: 'Sentiment Fingerprint',
      data: radarScores,
      backgroundColor: 'rgba(99, 102, 241, 0.2)',
      borderColor: '#6366f1',
      pointBackgroundColor: '#6366f1',
      borderWidth: 2,
    }]
  };

  return (
    <div className="dashboard-root">
      <div className="bg-glow"></div>
      
      {/* Restructured to "Command Center" Layout 
          [Main Content Area | Sticky Sidebar Log] 
      */}
      <main className="dashboard-layout" ref={reportRef}>
        
        <div className="main-content-area">
          <header className="dash-header anim-up">
            <div className="header-top">
              <button className="back-home-btn" onClick={() => navigate("/")}>Home</button>
              <div className="header-title-group">
                <h1 className="hero-title-small"><span className="text-gradient">GeoDrive</span> Command</h1>
                <p className="subtitle">Neural Sentiment & Spatial Intelligence</p>
              </div>
              <button className="export-btn" onClick={exportPDF}>Export PDF</button>
            </div>
          </header>

          {/* Input Section - Flex layout prevents button overlap */}
          <section className="card glass-card anim-up">
            <div className="input-wrapper">
              <textarea
                placeholder="Paste automotive text for neural analysis..."
                value={text}
                onChange={(e) => setText(e.target.value)}
                className="premium-textarea"
              />
              <div className="button-container-center">
                <button onClick={analyze} className="premium-btn" disabled={loading}>
                  {loading ? <span className="loader-small"></span> : "Analyze Neural Data"}
                </button>
              </div>
            </div>
          </section>

          {/* Map Section */}
          <div className="card map-box anim-up">
            <h3>Sentiment Heatmap</h3>
            <div className="map-wrapper" style={{ height: "400px", borderRadius: "24px", overflow: "hidden" }}>
              <MapContainer center={[18.5204, 73.8567]} zoom={8} style={{ height: "100%", width: "100%" }}>
                <TileLayer url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" />
                {history.map((item, i) => (
                  <CircleMarker 
                    key={i} 
                    center={[item.lat, item.lng]} 
                    pathOptions={{ color: item.markerColor, fillColor: item.markerColor, fillOpacity: 0.9, weight: 5 }}
                    radius={14}
                  >
                    <Popup>
                      <div style={{ color: '#000', textAlign: 'center' }}>
                        <strong>{item.brand.toUpperCase()}</strong><br/>
                        {item.sentiment.toUpperCase()}
                      </div>
                    </Popup>
                  </CircleMarker>
                ))}
              </MapContainer>
            </div>
          </div>

          {/* Charts Section */}
          <div className="charts-row">
            <div className="card chart-box anim-up">
              <h3>Sentiment Fingerprint</h3>
              <div className="chart-inner" style={{ height: "300px" }}>
                <Radar data={radarData} options={{ responsive: true, maintainAspectRatio: false }} />
              </div>
            </div>
            <div className="card chart-box anim-up delay-1">
              <h3>Brand Volume</h3>
              <div className="chart-inner" style={{ height: "300px" }}>
                <Bar
                  data={{
                    labels: brandData.map(b => b.brand),
                    datasets: [{ label: "Mentions", data: brandData.map(b => b.total_posts), backgroundColor: "#6366f1", borderRadius: 8 }]
                  }}
                  options={{ responsive: true, maintainAspectRatio: false }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* FEATURE: Sticky Sidebar Log - Highly User Friendly */}
        <aside className="activity-sidebar anim-up">
          <div className="card history-sidebar">
            <h3>Live Activity Feed</h3>
            <div className="history-list">
              {history.length === 0 && <p className="text-muted">Awaiting stream...</p>}
              {history.map((h, i) => (
                <div key={i} className="history-log-item">
                  <div className="log-header">
                    <span>{h.time}</span>
                    <span className={`pill ${h.sentiment.toLowerCase()}`}>{h.sentiment}</span>
                  </div>
                  <strong>{h.brand}</strong>
                  <p className="topic-text">Topic: {h.key_topic}</p>
                </div>
              ))}
            </div>
          </div>
        </aside>

      </main>
    </div>
  );
}