import React from 'react';
import './Approval.css';

const Approval = ({ onApprove, isLoading, approvalStatus }) => {
  const isApproved = approvalStatus === 'APPROVED';

  return (
    <div className="approval-container">
      <div className="approval-content">
        <h3>Approve Workflow</h3>
        <p>
          {isApproved
            ? 'This workflow has been approved. Agent cards and org charts can be generated.'
            : 'Approve this workflow to generate the agent org chart and tool registries required for implementation.'}
        </p>
      </div>
      <button
        className="approve-button"
        onClick={onApprove}
        disabled={isLoading || isApproved}
      >
        {isLoading ? 'Approving...' : (isApproved ? 'Approved' : 'Approve')}
      </button>
    </div>
  );
};

export default Approval;
