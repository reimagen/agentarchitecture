import React from 'react';
import StepCard from './StepCard';
import './StepsList.css';

function StepsList({ steps, registerStepRef }) {
  if (!steps || steps.length === 0) {
    return <div className="steps-list">No steps to display</div>;
  }

  return (
    <div className="steps-container">
      <h2>Workflow Steps</h2>
      <div className="steps-list">
        {steps.map((step, index) => (
          <StepCard
            key={step.id || index}
            step={step}
            ref={(element) =>
              registerStepRef && step.id ? registerStepRef(step.id, element) : null
            }
          />
        ))}
      </div>
    </div>
  );
}

export default StepsList;
