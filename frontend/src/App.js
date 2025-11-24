import React, { useCallback, useEffect, useRef, useState } from 'react';
import './App.css';
import FileUpload from './components/FileUpload';
import StepsList from './components/workflow-display/StepsList';
import SummaryContainer from './components/workflow-display/SummaryContainer';
import KeyInsights from './components/workflow-display/KeyInsights';
import AnalyzedWorkflowsList from './components/AnalyzedWorkflowsList';
import Approval from './components/workflow-actions/Approval'; // Import Approval component
import OrgGenerationCard from './components/workflow-actions/OrgGenerationCard'; // Import OrgGenerationCard component
import { prepareWorkflowBody } from './utils/fileProcessor';

const NEW_WORKFLOW_ID = '__new_workflow__';

function App() {
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [workflows, setWorkflows] = useState([]);
  const [sidebarLoading, setSidebarLoading] = useState(false);
  const [sidebarError, setSidebarError] = useState(null);
  const [selectedWorkflowId, setSelectedWorkflowId] = useState(NEW_WORKFLOW_ID);
  const [isApproving, setIsApproving] = useState(false); // State for approval button
  const [isGeneratingOrgAssets, setIsGeneratingOrgAssets] = useState(false); // State for org asset generation
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [isEditingWorkflowName, setIsEditingWorkflowName] = useState(false);
  const [workflowNameInput, setWorkflowNameInput] = useState('');
  const [isRenamingWorkflow, setIsRenamingWorkflow] = useState(false);
  const stepRefs = useRef({});
  const highlightTimeouts = useRef({});

  const WORKFLOW_API_BASE = 'http://localhost:8000/workflows';

  const fetchWorkflowList = useCallback(async () => {
    setSidebarLoading(true);
    setSidebarError(null);

    try {
      const response = await fetch(WORKFLOW_API_BASE);
      if (!response.ok) {
        throw new Error('Failed to load workflows');
      }

      const data = await response.json();
      setWorkflows(data.workflows || []);
    } catch (err) {
      setSidebarError(err.message);
    } finally {
      setSidebarLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchWorkflowList();
  }, [fetchWorkflowList]);

  const handleFileUpload = async (file) => {
    setLoading(true);
    setError(null);

    try {
      const body = await prepareWorkflowBody(file);

      const response = await fetch(WORKFLOW_API_BASE, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        throw new Error('Failed to analyze workflow');
      }

      const data = await response.json();
      setAnalysisResult(data);
      setSelectedWorkflowId(data.workflow_id);
      setShowDeleteConfirm(false);
      setIsEditingWorkflowName(false);
      fetchWorkflowList();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleWorkflowSelect = async (workflowId) => {
    if (!workflowId || workflowId === selectedWorkflowId) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${WORKFLOW_API_BASE}/${workflowId}`);
      if (!response.ok) {
        throw new Error('Failed to load workflow analysis');
      }

      const data = await response.json();
      setAnalysisResult((prevResult) => ({
        ...prevResult,
        workflow_id: workflowId,
        analysis: data.analysis,
        approvalStatus: data.approvalStatus,
        createdAt: data.createdAt,
        updatedAt: data.updatedAt,
        orgChart: data.orgChart,
        agentRegistry: data.agentRegistry,
        toolRegistry: data.toolRegistry,
        originalText: data.originalText ?? prevResult?.originalText,
        approvedAt: data.approvedAt ?? prevResult?.approvedAt,
        approvedBy: data.approvedBy ?? prevResult?.approvedBy,
        workflowName: data.workflowName ?? prevResult?.workflowName,
      }));
      setSelectedWorkflowId(workflowId);
      setShowDeleteConfirm(false);
      setIsEditingWorkflowName(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectNewWorkflow = () => {
    setSelectedWorkflowId(NEW_WORKFLOW_ID);
    setError(null);
    setShowDeleteConfirm(false);
     setIsEditingWorkflowName(false);
     setWorkflowNameInput('');
  };

  const handleApproveWorkflow = async () => {
    if (!selectedWorkflowId || selectedWorkflowId === NEW_WORKFLOW_ID) return;

    setIsApproving(true);
    setIsGeneratingOrgAssets(true); // Set generating state to true
    setError(null);

    try {
      const response = await fetch(`${WORKFLOW_API_BASE}/${selectedWorkflowId}/approve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ approved_by: 'frontend_user' }), // Example user
      });

      if (!response.ok) {
        throw new Error('Failed to approve workflow');
      }

      const data = await response.json();
      // Merge the approval response with the existing analysisResult to preserve the 'analysis' field
      setAnalysisResult((prevResult) => ({
        ...prevResult,
        ...data,
        workflowName: data.workflowName ?? prevResult?.workflowName,
      }));
      // Re-fetch the list to update the status badge in the sidebar
      fetchWorkflowList();
    } catch (err) {
      setError(err.message);
    } finally {
      setIsApproving(false);
      setIsGeneratingOrgAssets(false); // Reset generating state
    }
  };

  const handleStartDelete = () => {
    if (!analysisResult?.workflow_id) {
      return;
    }
    setShowDeleteConfirm(true);
  };

  const handleCancelDelete = () => {
    setShowDeleteConfirm(false);
  };

  const handleDeleteWorkflow = async () => {
    if (!selectedWorkflowId || selectedWorkflowId === NEW_WORKFLOW_ID) return;

    setIsDeleting(true);
    setError(null);

    try {
      const response = await fetch(`${WORKFLOW_API_BASE}/${selectedWorkflowId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete workflow');
      }

      setAnalysisResult(null);
      setSelectedWorkflowId(NEW_WORKFLOW_ID);
      setShowDeleteConfirm(false);
      setIsEditingWorkflowName(false);
      setWorkflowNameInput('');
      fetchWorkflowList();
    } catch (err) {
      setError(err.message);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleStartWorkflowNameEdit = () => {
    setWorkflowNameInput(analysisResult?.workflowName || '');
    setIsEditingWorkflowName(true);
  };

  const handleCancelWorkflowNameEdit = () => {
    setIsEditingWorkflowName(false);
    setWorkflowNameInput(analysisResult?.workflowName || '');
  };

  const handleSaveWorkflowName = async (event) => {
    if (event) {
      event.preventDefault();
    }

    if (!selectedWorkflowId || selectedWorkflowId === NEW_WORKFLOW_ID) {
      return;
    }

    const trimmedName = (workflowNameInput || '').trim();
    if (!trimmedName) {
      setError('Workflow name cannot be empty');
      return;
    }

    setIsRenamingWorkflow(true);
    setError(null);

    try {
      const response = await fetch(`${WORKFLOW_API_BASE}/${selectedWorkflowId}/name`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ workflow_name: trimmedName }),
      });

      if (!response.ok) {
        throw new Error('Failed to update workflow name');
      }

      const data = await response.json();
      setAnalysisResult((prevResult) =>
        prevResult
          ? {
              ...prevResult,
              workflowName: data.workflowName,
              updatedAt: data.updatedAt ?? prevResult.updatedAt,
            }
          : prevResult
      );
      setIsEditingWorkflowName(false);
      setWorkflowNameInput(data.workflowName || trimmedName);
      fetchWorkflowList();
    } catch (err) {
      setError(err.message);
    } finally {
      setIsRenamingWorkflow(false);
    }
  };

  const handleRegisterStepRef = useCallback((stepId, element) => {
    if (!stepId) return;
    if (element) {
      stepRefs.current[stepId] = element;
    } else {
      delete stepRefs.current[stepId];
    }
  }, []);

  const handleInsightStepClick = useCallback((stepId) => {
    if (!stepId) return;
    const target = stepRefs.current[stepId];
    if (!target) return;

    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    target.classList.add('highlight-step');

    if (highlightTimeouts.current[stepId]) {
      clearTimeout(highlightTimeouts.current[stepId]);
    }

    highlightTimeouts.current[stepId] = setTimeout(() => {
      target.classList.remove('highlight-step');
      delete highlightTimeouts.current[stepId];
    }, 1600);
  }, []);

  useEffect(() => {
    return () => {
      Object.values(highlightTimeouts.current).forEach((timeoutId) => clearTimeout(timeoutId));
      highlightTimeouts.current = {};
    };
  }, []);

  useEffect(() => {
    if (!isEditingWorkflowName) {
      setWorkflowNameInput(analysisResult?.workflowName || '');
    }
  }, [analysisResult?.workflowName, analysisResult?.workflow_id, isEditingWorkflowName]);

  console.log('Current analysisResult state:', analysisResult);
  const isUploadView = selectedWorkflowId === NEW_WORKFLOW_ID;
  const hasAnalysis = Boolean(analysisResult?.analysis) && !isUploadView;
  const workflowDisplayName = analysisResult?.workflowName || analysisResult?.workflow_id;

  return (
    <div className="App">
      <header className="App-header">
        <div className="nav-brand">Calibrate</div>
        <button
          type="button"
          className="btn btn--primary nav-new-workflow"
          onClick={handleSelectNewWorkflow}
          disabled={isUploadView}
        >
          Analyze New Workflow
        </button>
      </header>

      <div className="app-shell">
        <AnalyzedWorkflowsList
          workflows={workflows}
          loading={sidebarLoading}
          error={sidebarError}
          selectedWorkflowId={selectedWorkflowId}
          onSelect={handleWorkflowSelect}
        />

        <div className="app-content">
          <main className="App-main">
            {isUploadView ? (
              <div className="card card--spacious upload-panel">
                <h2 className="card-title">Analyze New Workflow</h2>
                <p>Upload a workflow file to analyze automation potential.</p>
                {error && <div className="error-message">{error}</div>}
                <FileUpload onFileUpload={handleFileUpload} loading={loading} />
              </div>
            ) : hasAnalysis ? (
              <>
                {error && <div className="error-message">{error}</div>}
                <div className="workflow-detail-header">
                  {isEditingWorkflowName ? (
                    <form className="workflow-title-form" onSubmit={handleSaveWorkflowName}>
                      <label htmlFor="workflow-title-input" className="workflow-title-label">
                        Workflow:
                      </label>
                      <input
                        id="workflow-title-input"
                        type="text"
                        className="workflow-title-input"
                        value={workflowNameInput}
                        onChange={(e) => setWorkflowNameInput(e.target.value)}
                        maxLength={80}
                        placeholder="Enter workflow name"
                        disabled={isRenamingWorkflow}
                      />
                      <div className="workflow-title-actions">
                        <button
                          type="button"
                          className="btn btn--neutral"
                          onClick={handleCancelWorkflowNameEdit}
                          disabled={isRenamingWorkflow}
                        >
                          Cancel
                        </button>
                        <button
                          type="submit"
                          className="btn btn--success"
                          disabled={isRenamingWorkflow}
                        >
                          {isRenamingWorkflow ? 'Saving...' : 'Save'}
                        </button>
                      </div>
                    </form>
                  ) : (
                    <>
                      <div className="workflow-title-display">
                        <span className="workflow-title-label">Workflow:</span>
                        <h2 className="workflow-detail-title">
                          {workflowDisplayName || 'Workflow Details'}
                        </h2>
                      </div>
                      <button
                        type="button"
                        className="workflow-title-edit"
                        onClick={handleStartWorkflowNameEdit}
                        disabled={!analysisResult?.workflow_id}
                        aria-label="Edit workflow name"
                      >
                        ✏️
                      </button>
                    </>
                  )}
                </div>
                <div className="results-container">
                  <div className="results-grid">
                    <div className="left-panel">
                      <div className="card card--compact">
                        <StepsList
                          steps={analysisResult.analysis.steps}
                          registerStepRef={handleRegisterStepRef}
                        />
                      </div>
                    </div>
                    <div className="right-panel">
                      <div className="card card--compact">
                        <SummaryContainer summary={analysisResult.analysis.summary} />
                      </div>
                      <div className="card card--compact">
                        <KeyInsights
                          insights={analysisResult.analysis.key_insights}
                          onStepClick={handleInsightStepClick}
                        />
                      </div>
                      {(analysisResult.approvalStatus === 'PENDING' || analysisResult.approvalStatus === 'APPROVED') && (
                        <div className="card card--compact">
                          <Approval
                            onApprove={handleApproveWorkflow}
                            isLoading={isApproving}
                            approvalStatus={analysisResult.approvalStatus}
                          />
                        </div>
                      )}
                      {analysisResult && (
                        <div className="card card--compact">
                          <OrgGenerationCard
                            approvalStatus={analysisResult.approvalStatus}
                            orgChart={analysisResult.orgChart}
                            agentRegistry={analysisResult.agentRegistry}
                            toolRegistry={analysisResult.toolRegistry}
                            isGenerating={isGeneratingOrgAssets}
                          />
                        </div>
                      )}
                      <div className="card card--compact delete-workflow-section">
                        {showDeleteConfirm ? (
                          <div className="delete-confirm-card">
                            <p className="delete-confirm-text">
                              Are you sure you want to delete this workflow? This action cannot be undone.
                            </p>
                            <div className="delete-confirm-actions">
                              <button
                                type="button"
                                className="btn btn--neutral"
                                onClick={handleCancelDelete}
                                disabled={isDeleting}
                              >
                                Cancel
                              </button>
                              <button
                                type="button"
                                className="btn btn--danger"
                                onClick={handleDeleteWorkflow}
                                disabled={isDeleting}
                              >
                                {isDeleting ? 'Deleting…' : 'Delete'}
                              </button>
                            </div>
                          </div>
                        ) : (
                          <button
                            type="button"
                            className="btn btn--danger delete-workflow-button"
                            onClick={handleStartDelete}
                            disabled={isDeleting || !analysisResult?.workflow_id}
                          >
                            <span className="delete-icon" aria-hidden="true">🗑️</span>
                            Delete Workflow
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="card card--spacious placeholder-panel">
                {loading ? (
                  <p>Loading workflow analysis...</p>
                ) : (
                  <p>Select a workflow from the sidebar to view its analysis.</p>
                )}
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
  );
}

export default App;
