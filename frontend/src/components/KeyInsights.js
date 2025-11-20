import React, { useState } from 'react';
import './KeyInsights.css';

function KeyInsights({ insights }) {
  const [expandedIndex, setExpandedIndex] = useState(null);

  if (!insights || insights.length === 0) {
    return <div className="insights-container">No insights available</div>;
  }

  const getPriorityColor = (priority) => {
    switch (priority?.toUpperCase()) {
      case 'HIGH':
        return '#dc3545';
      case 'MEDIUM':
        return '#ffc107';
      case 'LOW':
        return '#28a745';
      default:
        return '#6c757d';
    }
  };

  const getPriorityIcon = (priority) => {
    switch (priority?.toUpperCase()) {
      case 'HIGH':
        return '🔴';
      case 'MEDIUM':
        return '🟡';
      case 'LOW':
        return '🟢';
      default:
        return '⚪';
    }
  };

  return (
    <div className="insights-container">
      <h2>Key Insights</h2>
      <div className="insights-list">
        {insights.map((insight, index) => (
          <div
            key={index}
            className="insight-card"
            style={{
              borderLeftColor: getPriorityColor(insight.priority),
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
                  {getPriorityIcon(insight.priority)}
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
                        <span key={stepIndex} className="step-tag">
                          {step}
                        </span>
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
