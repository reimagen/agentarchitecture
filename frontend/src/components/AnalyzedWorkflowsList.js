import React from 'react';
import './AnalyzedWorkflowsList.css';

function AnalyzedWorkflowsList({
  workflows,
  selectedWorkflowId,
  onSelect,
  onSelectNewWorkflow,
  isNewWorkflowSelected,
  loading,
  error,
}) {
  return (
    <aside className="analyzed-workflows">
      <button
        type="button"
        className={`analyzed-workflows__new-button ${
          isNewWorkflowSelected ? 'is-active' : ''
        }`}
        onClick={() => onSelectNewWorkflow && onSelectNewWorkflow()}
      >
        + Analyze New Workflow
      </button>

      <div className="analyzed-workflows__header">
        <h2>Previous Analyses</h2>
        {loading && <span className="analyzed-workflows__status">Loading…</span>}
      </div>

      {error && <div className="analyzed-workflows__error">{error}</div>}

      {!loading && workflows.length === 0 && (
        <p className="analyzed-workflows__empty">No analyses yet. Upload a workflow to get started.</p>
      )}

      <ul className="analyzed-workflows__list">
        {workflows.map((workflow) => (
          <li key={workflow.workflow_id}>
            <button
              type="button"
              className={`analyzed-workflows__item ${
                selectedWorkflowId === workflow.workflow_id ? 'is-active' : ''
              }`}
              onClick={() => onSelect(workflow.workflow_id)}
            >
              <span className="analyzed-workflows__item-id">
                {workflow.workflowName || workflow.workflow_id}
              </span>
              <span className="analyzed-workflows__item-meta">
                {workflow.createdAt ? new Date(workflow.createdAt).toLocaleString() : 'Unknown date'}
              </span>
              {workflow.approvalStatus && (
                <span className={`analyzed-workflows__badge status-${workflow.approvalStatus.toLowerCase()}`}>
                  {workflow.approvalStatus}
                </span>
              )}
            </button>
          </li>
        ))}
      </ul>
    </aside>
  );
}

export default AnalyzedWorkflowsList;
