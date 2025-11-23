import React from 'react';
import './Meter.css';

const Meter = ({ value = 0 }) => {
  const percentage = Math.round(value * 100);

  const getAutomationColor = (score) => {
    if (score >= 0.7) return '#28a745'; // green
    if (score >= 0.5) return '#ffc107'; // yellow
    return '#dc3545'; // red
  };

  return (
    <div className="meter-container">
      <div className="meter-label">Automation Potential</div>
      <div className="meter-bar">
        <div 
          className="meter-fill" 
          style={{ 
            width: `${percentage}%`,
            backgroundColor: getAutomationColor(value)
          }}
        />
      </div>
      <div className="meter-text">{percentage}%</div>
    </div>
  );
};

export default Meter;
