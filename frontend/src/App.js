import React, { useCallback, useEffect, useState } from 'react';
import './App.css';
import FileUpload from './components/FileUpload';
import StepsList from './components/StepsList';
import SummaryContainer from './components/SummaryContainer';
import KeyInsights from './components/KeyInsights';
import AnalyzedWorkflowsList from './components/AnalyzedWorkflowsList';
import Approval from './components/Approval'; // Import Approval component
import { prepareWorkflowBody } from './utils/fileProcessor';

function App() {
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [workflows, setWorkflows] = useState([]);
  const [sidebarLoading, setSidebarLoading] = useState(false);
  const [sidebarError, setSidebarError] = useState(null);
  const [selectedWorkflowId, setSelectedWorkflowId] = useState(null);
  const [isApproving, setIsApproving] = useState(false); // State for approval button

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
      setAnalysisResult({
        // The list endpoint only returns a subset of fields, so we need to merge
        // what we get from the detail endpoint into the full analysisResult structure
        ...analysisResult,
        workflow_id: workflowId,
        analysis: data.analysis,
        approvalStatus: data.approvalStatus,
        createdAt: data.createdAt,
        updatedAt: data.updatedAt,
      });
      setSelectedWorkflowId(workflowId);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleApproveWorkflow = async () => {
    if (!selectedWorkflowId) return;

    setIsApproving(true);
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
      }));
      // Re-fetch the list to update the status badge in the sidebar
      fetchWorkflowList();
    } catch (err) {
      setError(err.message);
    } finally {
      setIsApproving(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Workflow Analyzer</h1>
        <p>Upload a workflow file to analyze automation potential</p>
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
            <FileUpload onFileUpload={handleFileUpload} loading={loading} />

            {error && <div className="error-message">{error}</div>}

            {analysisResult && analysisResult.analysis && (
              <div className="results-container">
                <div className="results-grid">
                  <div className="left-panel">
                    <StepsList steps={analysisResult.analysis.steps} />
                  </div>
                  <div className="right-panel">
                    <SummaryContainer summary={analysisResult.analysis.summary} />
                    <KeyInsights insights={analysisResult.analysis.key_insights} />
                    {(analysisResult.approvalStatus === 'PENDING' || analysisResult.approvalStatus === 'APPROVED') && (
                      <Approval
                        onApprove={handleApproveWorkflow}
                        isLoading={isApproving}
                        approvalStatus={analysisResult.approvalStatus}
                      />
                    )}
                  </div>
                </div>
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
  );
}

export default App;