import React, { useState } from 'react';
import './KeyInsights.css';

function KeyInsights({ insights, onStepClick }) {
  const [expandedIndex, setExpandedIndex] = useState(null);

  if (!insights || insights.length === 0) {
    return <div className="insights-container">No insights available</div>;
  }

  const getInsightColor = (priority, title) => {
    if (title.includes("Strong Automation Potential")) {
      return '#28a745'; // Green for strong
    }
    if (title.includes("Critical Compliance Risks")) {
      return '#dc3545'; // Red for critical
    }
    if (title.includes("Manual Review Bottleneck")) {
      return '#ffc107'; // Yellow for bottleneck
    }

    // Default mapping for other insights or if keywords not found
    switch (priority?.toUpperCase()) {
      case 'LOW':
        return '#28a745'; // Green
      case 'MEDIUM':
        return '#ffc107'; // Yellow
      case 'HIGH':
        return '#dc3545'; // Red
      case 'CRITICAL':
        return '#dc3545'; // Red
      default:
        return '#6c757d'; // Grey default
    }
  };

  const getInsightIcon = (priority, title) => {
    if (title.includes("Strong Automation Potential")) {
      return '🟢'; // Green circle for strong
    }
    if (title.includes("Critical Compliance Risks")) {
      return '🔴'; // Red circle for critical
    }
    if (title.includes("Manual Review Bottleneck")) {
      return '🟡'; // Yellow circle for bottleneck
    }

    // Default mapping for other insights or if keywords not found
    switch (priority?.toUpperCase()) {
      case 'LOW':
        return '🟢'; // Green circle
      case 'MEDIUM':
        return '🟡'; // Yellow circle
      case 'HIGH':
        return '🔴'; // Red circle
      case 'CRITICAL':
        return '🔴'; // Red circle
      default:
        return '⚪'; // White/Grey default
    }
  };

  return (
    <div className="insights-container">
      <h2 className="card-title">Key Insights</h2>
      <div className="insights-list">
        {insights.map((insight, index) => (
          <div
            key={index}
            className="insight-card"
            style={{
              borderLeftColor: getInsightColor(insight.priority, insight.title),
            }}
          >
            <div
              className="insight-header"
              onClick={() =>
                setExpandedIndex(expandedIndex === index ? null : index)
              }
            >
              <div className="insight-title-section">
                <span className="priority-icon">
                  {getInsightIcon(insight.priority, insight.title)}
                </span>
                <div>
                  <h3 className="insight-title">{insight.title}</h3>
                  <p className="insight-description">{insight.description}</p>
                </div>
              </div>
              <button className="expand-button">
                {expandedIndex === index ? '−' : '+'}
              </button>
            </div>

            {expandedIndex === index && (
              <div className="insight-details">
                <div className="affected-steps">
                  <h4>Affected Steps:</h4>
                  <div className="step-tags">
                    {insight.affected_steps &&
                      insight.affected_steps.map((step, stepIndex) => (
                        <button
                          key={stepIndex}
                          type="button"
                          className="step-tag"
                          onClick={() => onStepClick && onStepClick(step)}
                        >
                          {step}
                        </button>
                      ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default KeyInsights;
