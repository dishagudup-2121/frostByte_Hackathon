import { useState, useEffect } from "react";
import axios from "axios";
import { Bar } from "react-chartjs-2";
import "chart.js/auto";

const API = "http://127.0.0.1:8000";

export default function App() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [brandData, setBrandData] = useState([]);

  // Analyze text with device location
  const analyze = async () => {
    if (!text) return alert("Enter some text");

    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        try {
          const res = await axios.post(`${API}/ai/analyze`, {
            text,
            latitude: pos.coords.latitude,
            longitude: pos.coords.longitude,
          });

          setResult(res.data);
          fetchAnalytics();
        } catch (err) {
          console.error(err);
          alert("Backend error");
        }
      },
      () => {
        alert("Location permission denied");
      }
    );
  };

  // Fetch analytics
  const fetchAnalytics = async () => {
    try {
      const res = await axios.get(`${API}/analytics/brand-summary`);
      setBrandData(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  return (
    <div style={{ padding: 30 }}>
      <h2>🚗 Automotive AI Dashboard</h2>

      <textarea
        placeholder="Enter automotive social media text..."
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={4}
        cols={50}
      />
      <br />
      <button onClick={analyze}>Analyze</button>

      {result && (
        <div>
          <h3>AI Result</h3>
          <p>Brand: {result.brand}</p>
          <p>Sentiment: {result.sentiment}</p>
          <p>Confidence: {result.confidence}</p>
          <p>Topic: {result.key_topic}</p>
        </div>
      )}

      <h3>Brand Analytics</h3>
      <Bar
        data={{
          labels: brandData.map((b) => b.brand),
          datasets: [
            {
              label: "Total Posts",
              data: brandData.map((b) => b.total_posts),
              backgroundColor: "blue",
            },
          ],
        }}
      />
    </div>
  );
}
