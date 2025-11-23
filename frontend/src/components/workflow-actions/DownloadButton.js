import React from 'react';

const DownloadButton = ({ fileName, jsonContent, buttonText = "Download JSON" }) => {
  const handleDownload = () => {
    if (!jsonContent) {
      console.error("No content to download.");
      return;
    }

    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(jsonContent, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", fileName);
    document.body.appendChild(downloadAnchorNode); // Required for Firefox
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  };

  return (
    <button onClick={handleDownload} disabled={!jsonContent}>
      {buttonText}
    </button>
  );
};

export default DownloadButton;
