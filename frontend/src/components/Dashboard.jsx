import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { Bar, Radar } from "react-chartjs-2";
import "chart.js/auto";
import "../App.css";

const API = "http://127.0.0.1:8000";

export default function Dashboard() {
  const navigate = useNavigate();
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [brandData, setBrandData] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Initial Radar scores (neutral 50)
  const [radarScores, setRadarScores] = useState([50, 50, 50, 50, 50, 50, 50, 50, 50, 50]);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const res = await axios.get(`${API}/analytics/brand-summary`);
      setBrandData(res.data);
    } catch (err) {
      console.error("Analytics fetch failed:", err);
    }
  };

  // Maps AI analysis to Radar Chart spikes
  const updateRadar = (data) => {
    const TOPICS = ['mileage', 'engine', 'service', 'price', 'comfort', 'performance', 'design', 'safety', 'features', 'other'];
    const index = TOPICS.indexOf(data.key_topic.toLowerCase());
    
    if (index !== -1) {
      const newScores = [...radarScores];
      // Positive (95), Neutral (60), Negative (20)
      newScores[index] = data.sentiment === "positive" ? 95 : data.sentiment === "negative" ? 20 : 60;
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
        setResult(res.data);
        updateRadar(res.data);
        fetchAnalytics();
      } catch (err) {
        console.error("Analysis failed:", err);
      } finally {
        setLoading(false);
      }
    });
  };

  const radarData = {
    labels: ['Mileage', 'Engine', 'Service', 'Price', 'Comfort', 'Performance', 'Design', 'Safety', 'Features', 'Other'],
    datasets: [{
      label: 'Neural Attribute Rating',
      data: radarScores,
      fill: true,
      backgroundColor: 'rgba(99, 102, 241, 0.2)',
      borderColor: '#6366f1',
      pointBackgroundColor: '#6366f1',
      borderWidth: 3,
      pointRadius: 4
    }]
  };

  return (
    <div className="dashboard-root">
      <div className="bg-glow"></div>
      
      <main className="dashboard-container">
        {/* Navigation Header */}
        <header className="dash-header anim-up">
          <div className="header-top">
            <button className="back-home-btn" onClick={() => navigate("/")}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                <polyline points="9 22 9 12 15 12 15 22"></polyline>
              </svg>
              Home
            </button>
            <div className="header-title-group">
              <h1 className="hero-title-small"><span className="text-gradient">Intelligence</span> Hub</h1>
              <p className="subtitle">Real-time Automotive Sentiment Engine</p>
            </div>
            <div style={{ width: '100px' }}></div> {/* Keeps title centered */}
          </div>
        </header>

        {/* Input Card */}
        <section className="card glass-card anim-up">
          <div className="input-group">
            <textarea
              placeholder="Paste automotive feedback (e.g., 'The Porsche engine sounds powerful but the price is too high')..."
              value={text}
              onChange={(e) => setText(e.target.value)}
              className="premium-textarea"
            />
            <div className="button-container-center">
              <button onClick={analyze} className="premium-btn" disabled={loading}>
                {loading ? (
                  <span className="loader-small"></span>
                ) : (
                  <>
                    Run Neural Analysis
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{marginLeft: '10px'}}>
                      <line x1="22" y1="2" x2="11" y2="13"></line>
                      <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                    </svg>
                  </>
                )}
              </button>
            </div>
          </div>
        </section>

        {/* Real-time Insights Bar */}
        {result && (
          <div className="insights-grid anim-up">
            <div className="insight-box"><small>Brand</small><strong>{result.brand}</strong></div>
            <div className="insight-box"><small>Sentiment</small><strong className={result.sentiment.toLowerCase()}>{result.sentiment}</strong></div>
            <div className="insight-box"><small>Confidence</small><strong>{(result.confidence * 100).toFixed(1)}%</strong></div>
            <div className="insight-box"><small>Key Topic</small><strong>{result.key_topic}</strong></div>
          </div>
        )}

        {/* Analytics Visualization Section */}
        
        <div className="charts-row">
          <div className="card chart-box anim-up">
            <h3>Market Volume by Brand</h3>
            <div className="chart-inner">
              <Bar
                data={{
                  labels: brandData.map(b => b.brand),
                  datasets: [{
                    label: "Mentions",
                    data: brandData.map(b => b.total_posts),
                    backgroundColor: "#6366f1",
                    borderRadius: 8,
                  }]
                }}
                options={{ 
                  responsive: true, 
                  maintainAspectRatio: false,
                  plugins: { legend: { display: false } }
                }}
              />
            </div>
          </div>

          <div className="card chart-box anim-up delay-1">
            <h3>Sentiment Fingerprint</h3>
            <div className="chart-inner">
              <Radar 
                data={radarData}
                options={{ 
                  responsive: true, 
                  maintainAspectRatio: false,
                  scales: { 
                    r: { 
                      grid: { color: 'rgba(255,255,255,0.05)' }, 
                      angleLines: { color: 'rgba(255,255,255,0.1)' },
                      pointLabels: { color: '#94a3b8', font: { size: 11 } },
                      ticks: { display: false },
                      suggestedMin: 0,
                      suggestedMax: 100
                    } 
                  }
                }} 
              />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}