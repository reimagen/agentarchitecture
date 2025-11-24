import React from 'react';
import './OrgGenerationCard.css';
import DownloadButton from './DownloadButton'; // Assuming DownloadButton is in the same directory
import DownloadIcon from '../icons/DownloadIcon'; // Import DownloadIcon

const OrgGenerationCard = ({ approvalStatus, orgChart, agentRegistry, toolRegistry, isGenerating }) => {
  const isApproved = approvalStatus === 'APPROVED';

  return (
    <div className={`org-generation-card ${!isApproved || isGenerating ? 'disabled' : ''}`}>
      <h3 className="card-title">Agent Organization Assets</h3>
      {isGenerating ? (
        <p className="status-message generating-message">Generating Org Assets...</p>
      ) : !isApproved ? (
        <p className="status-message">Workflow must be approved to generate these assets.</p>
      ) : (
        <>
          <p>Download the generated Agent Organization Chart, Agent Cards, and Tool Registries.</p>
          <div className="download-buttons">
            {orgChart && (
              <DownloadButton
                fileName="org_chart.json"
                jsonContent={orgChart}
                buttonText="Download Org Chart JSON"
                icon={DownloadIcon}
              />
            )}
            {agentRegistry && Object.keys(agentRegistry).length > 0 && (
              <DownloadButton
                fileName="agent_cards.json"
                jsonContent={agentRegistry}
                buttonText="Download Agent Cards JSON"
                icon={DownloadIcon}
              />
            )}
            {toolRegistry && (
              <DownloadButton
                fileName="tool_registries.json"
                jsonContent={toolRegistry}
                buttonText="Download Tool Registries JSON"
                icon={DownloadIcon}
              />
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default OrgGenerationCard;
