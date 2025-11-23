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

  const formatStepId = (id) => {
    if (!id || !id.startsWith('step_')) {
      return id; // Return original if not in expected format
    }
    const stepNumber = id.split('_')[1];
    return `Step ${stepNumber}`;
  };

  return (
    <div className="step-card">
      <div className="card-header">
        <div className="card-left-section">
          <h3 className="step-id">{formatStepId(step.id)}</h3>
          <p className="step-description">{step.description}</p>
        </div>
        <div className="card-badges">
          <div>
            <span
              className="badge risk-badge"
              style={{
                backgroundColor: getRiskColor(step.risk_level),
                color: 'white',
                borderColor: getRiskColor(step.risk_level),
              }}
            >
              Risk: {step.risk_level}
            </span>
          </div>
          {step.requires_human_review && (
            <div className="human-review-wrapper">
              <span className="badge human-review-badge">Needs Human Review</span>
            </div>
          )}
        </div>
      </div>

      <div className="step-metrics">
        <div className="metric">
          <span className="metric-label">Automation Compatibility:</span>
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
          <div className="metric-bar">
            <div
              className="metric-fill"
              style={{
                width: `${(step.determinism_score || 0) * 100}%`,
                backgroundColor: getAutomationColor(step.determinism_score), // Use getAutomationColor
              }}
            />
          </div>
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
