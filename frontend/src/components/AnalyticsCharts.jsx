import React from "react";
import {
  LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip,
  PieChart, Pie, Cell
} from "recharts";

export default function AnalyticsCharts({ data }) {

  if (!data) return <p>No analytics yet</p>;

  const sentimentTrend = data.review_volume_trend || [];
  const priceTrend = data.price_history || [];
  const topicData = data.top_topics || [];

  const COLORS = ["#00C49F", "#FF8042", "#0088FE", "#FFBB28"];

  return (
    <div style={{ display: "flex", gap: "40px", flexWrap: "wrap" }}>

      {/* Sentiment Trend */}
      <div>
        <h3>Review Trend</h3>
        <LineChart width={400} height={250} data={sentimentTrend}>
          <Line type="monotone" dataKey="count" stroke="#00C49F" />
          <CartesianGrid stroke="#ccc" />
          <XAxis dataKey="month" />
          <YAxis />
          <Tooltip />
        </LineChart>
      </div>

      {/* Price Trend */}
      <div>
        <h3>Price Trend</h3>
        <LineChart width={400} height={250} data={priceTrend}>
          <Line type="monotone" dataKey="price" stroke="#FF8042" />
          <CartesianGrid stroke="#ccc" />
          <XAxis dataKey="month" />
          <YAxis />
          <Tooltip />
        </LineChart>
      </div>

      {/* Topic Pie */}
      <div>
        <h3>Topic Distribution</h3>
        <PieChart width={350} height={250}>
          <Pie
            data={topicData}
            dataKey="count"
            nameKey="topic"
            cx="50%"
            cy="50%"
            outerRadius={80}
            label
          >
            {topicData.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </div>

    </div>
  );
}
