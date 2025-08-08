import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import SeriesChart from './components/SeriesChart';
import HealthDashboard from './components/HealthDashboard';

export default function App(){
  return (
    <Router>
      <div style={{padding: 16}}>
        <h1>MacroPulse Dashboard</h1>
        <nav style={{marginBottom: 16}}>
          <Link to="/charts" style={{marginRight: 12}}>Charts</Link>
          <Link to="/health">Data Health</Link>
        </nav>
        <Routes>
          <Route path="/" element={<Navigate to="/charts" />} />
          <Route path="/charts" element={
            <div>
              <SeriesChart code="FEDFUNDS" />
              <SeriesChart code="UNRATE" />
              <SeriesChart code="CPIAUCSL" />
              <SeriesChart code="GDPC1" />
            </div>
          }/>
          <Route path="/health" element={<HealthDashboard />} />
        </Routes>
      </div>
    </Router>
  );
}
