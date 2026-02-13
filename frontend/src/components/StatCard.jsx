export default function StatCard({ title, value }) {
  return (
    <div style={{
      padding: "20px",
      borderRadius: "12px",
      background: "#1e293b",
      color: "white",
      transition: "0.3s"
    }}>
      <h4>{title}</h4>
      <h2>{value}</h2>
    </div>
  );
}
