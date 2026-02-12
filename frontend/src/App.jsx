import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

// Centralized Imports for your new component structure
import Home from "./components/Home";
import Dashboard from "./components/Dashboard";

// Global premium styles
import "./App.css";

function App() {
  return (
    <Router>
      <div className="app-root">
        <Routes>
          {/* Hero Landing Page: The first impression for judges */}
          <Route path="/" element={<Home />} />

          {/* AI Sentiment Dashboard: The core data engine */}
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;