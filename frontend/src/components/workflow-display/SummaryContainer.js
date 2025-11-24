import React from 'react';
import './SummaryContainer.css';
import Meter from './Meter'; // Import the new Meter component

function SummaryContainer({ summary }) {
  if (!summary) {
    return <div className="summary-container">No summary data available</div>;
  }

  const stats = [
    {
      label: 'Total Steps',
      value: summary.total_steps,
      icon: '📋',
    },
    {
      label: 'Automatable Steps',
      value: summary.automatable_count,
      icon: '⚙️',
    },
    {
      label: 'Agent Compatible',
      value: summary.agent_required_count,
      icon: '🤖',
    },
    {
      label: 'Requires Human',
      value: summary.human_required_count,
      icon: '👤',
    },
    {
      label: 'High Risk',
      value: summary.high_risk_steps,
      icon: '⚠️',
    },
    {
      label: 'Critical Risk',
      value: summary.critical_risk_steps,
      icon: '🔴',
    },
  ];

  return (
    <div className="summary-container">
      <h2 className="card-title">Summary</h2>
      <div className="summary-grid">
        {stats.map((stat, index) => (
          <div key={index} className="summary-stat">
            <div className="stat-icon">{stat.icon}</div>
            <div className="stat-content">
              <div className="stat-value">{stat.value}</div>
              <div className="stat-label">{stat.label}</div>
              {stat.subtitle && <div className="stat-subtitle">{stat.subtitle}</div>}
            </div>
          </div>
        ))}
      </div>

      {summary.automation_summary?.overall_assessment && (
        <div className="overall-assessment">
          <h3>Overall Assessment</h3>
          <p>{summary.automation_summary.overall_assessment}</p>
        </div>
      )}
      
      <div className="automation-potential">
        <h3>Full Automation Potential</h3>
        <Meter value={summary.automation_potential || 0} />
      </div>

    </div>
  );
}

export default SummaryContainer;
