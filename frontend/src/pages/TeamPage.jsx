import React from "react";




export default function TeamPage() {
  const team = [
    {
      name: "Bhavikesh Hedau",
      role: "Frontend Developer",
      info: "Worked on Competitive Insights UI"
    },
    {
      name: "Disha Gudup",
      role: "Backend Developer",
      info: "Handled FastAPI APIs"
    },
    {
      name: "Vidula Gote",
      role: "Database Engineer",
      info: "Managed Supabase integration"
    },
    {
      name: "Chaitanya Hapse",
      role: "AI/Analytics",
      info: "Built sentiment & analytics logic"
    },
    {
      name: "Harshal Ramteke",
      role: "Deployment/Testing",
      info: "Deployment & testing support"
    }
  ];

  return (
    <div style={{ padding: "40px" }}>
              <button
        className="back-btn"
        onClick={() => window.location.href = "/dashboard"}
      >
        ← Back to Dashboard
      </button>
      <h1 className="hero-title-small">
        <span className="text-gradient">Our</span> Team
      </h1>

      {team.map((member, i) => (
        <div key={i} className="card" style={{ marginTop: "20px" }}>
          <h3>{member.name}</h3>
          <p><b>Role:</b> {member.role}</p>
          <p>{member.info}</p>
        </div>
      ))}
    </div>
  );
}
