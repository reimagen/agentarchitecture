import React, { useCallback, useEffect, useState } from 'react';
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
      }));
      setSelectedWorkflowId(workflowId);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectNewWorkflow = () => {
    setSelectedWorkflowId(NEW_WORKFLOW_ID);
    setError(null);
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

  console.log('Current analysisResult state:', analysisResult);
  const isUploadView = selectedWorkflowId === NEW_WORKFLOW_ID;
  const hasAnalysis = Boolean(analysisResult?.analysis) && !isUploadView;

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
          onSelectNewWorkflow={handleSelectNewWorkflow}
          isNewWorkflowSelected={isUploadView}
          onSelect={handleWorkflowSelect}
        />

        <div className="app-content">
          <main className="App-main">
            {isUploadView ? (
              <div className="upload-panel">
                <h2>Analyze New Workflow</h2>
                <p>Upload a JSON, TXT, or YAML file to run a fresh workflow analysis.</p>
                {error && <div className="error-message">{error}</div>}
                <FileUpload onFileUpload={handleFileUpload} loading={loading} />
              </div>
            ) : hasAnalysis ? (
              <>
                {error && <div className="error-message">{error}</div>}
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
                      {analysisResult && (
                        <OrgGenerationCard
                          approvalStatus={analysisResult.approvalStatus}
                          orgChart={analysisResult.orgChart}
                          agentRegistry={analysisResult.agentRegistry}
                          toolRegistry={analysisResult.toolRegistry}
                          isGenerating={isGeneratingOrgAssets}
                        />
                      )}
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="placeholder-panel">
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
