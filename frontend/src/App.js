import React, { useState } from 'react';
import './App.css';
import FileUpload from './components/FileUpload';
import StepsList from './components/StepsList';
import SummaryContainer from './components/SummaryContainer';
import KeyInsights from './components/KeyInsights';
import { prepareWorkflowBody } from './utils/fileProcessor';

function App() {
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileUpload = async (file) => {
    setLoading(true);
    setError(null);

    try {
      const body = await prepareWorkflowBody(file);

      // Update this URL to match your backend endpoint
      const response = await fetch('http://localhost:8000/workflows', {
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
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Workflow Analyzer</h1>
        <p>Upload a workflow file to analyze automation potential</p>
      </header>

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
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
