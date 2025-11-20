import React, { useRef } from 'react';
import './FileUpload.css';

function FileUpload({ onFileUpload, loading }) {
  const fileInputRef = useRef(null);

  const handleClick = () => {
    fileInputRef.current.click();
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      onFileUpload(file);
    }
  };

  return (
    <div className="file-upload-container">
      <button
        className="upload-button"
        onClick={handleClick}
        disabled={loading}
      >
        {loading ? 'Analyzing...' : '📁 Upload Workflow File'}
      </button>
      <input
        ref={fileInputRef}
        type="file"
        onChange={handleFileChange}
        accept=".json,.txt,.yaml,.yml"
        style={{ display: 'none' }}
      />
      <p className="upload-hint">Supported formats: JSON, TXT, YAML</p>
    </div>
  );
}

export default FileUpload;
