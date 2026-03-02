import axios from "axios";

const API = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export const getBrandTrend = async (brand) => {
  try {
    const res = await axios.get(`${API}/analytics/trend/${brand}`);
    return res.data;
  } catch (err) {
    console.error("Trend API error:", err);
    return null;
  }
};
