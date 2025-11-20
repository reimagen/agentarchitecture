import React from 'react';
import './StepCard.css';

function StepCard({ step }) {
  const getRiskColor = (riskLevel) => {
    switch (riskLevel?.toLowerCase()) {
      case 'critical':
        return '#dc3545';
      case 'high':
        return '#fd7e14';
      case 'medium':
        return '#ffc107';
      case 'low':
        return '#28a745';
      default:
        return '#6c757d';
    }
  };

  const getAutomationColor = (score) => {
    if (score >= 0.8) return '#28a745';
    if (score >= 0.6) return '#ffc107';
    return '#dc3545';
  };

  return (
    <div className="step-card">
      <div className="card-header">
        <h3 className="step-id">{step.id}</h3>
        <div className="card-badges">
          <span className="badge risk-badge" style={{ borderColor: getRiskColor(step.risk_level) }}>
            {step.risk_level}
          </span>
          {step.requires_human_review && (
            <span className="badge human-review-badge">🧑 Human Review</span>
          )}
        </div>
      </div>

      <p className="step-description">{step.description}</p>

      <div className="step-metrics">
        <div className="metric">
          <span className="metric-label">Automation:</span>
          <div className="metric-bar">
            <div
              className="metric-fill"
              style={{
                width: `${(step.automation_feasibility || 0) * 100}%`,
                backgroundColor: getAutomationColor(step.automation_feasibility),
              }}
            />
          </div>
          <span className="metric-value">{Math.round((step.automation_feasibility || 0) * 100)}%</span>
        </div>

        <div className="metric">
          <span className="metric-label">Determinism:</span>
          <span className="metric-value">{Math.round((step.determinism_score || 0) * 100)}%</span>
        </div>

        <div className="metric">
          <span className="metric-label">Agent Type:</span>
          <span className="metric-value">{step.agent_type || 'N/A'}</span>
        </div>
      </div>

      {step.suggested_tools && step.suggested_tools.length > 0 && (
        <div className="tools-section">
          <span className="tools-label">Tools:</span>
          <div className="tools-list">
            {step.suggested_tools.map((tool, index) => (
              <span key={index} className="tool-tag">
                {tool}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default StepCard;
