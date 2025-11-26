/**
 * Service for connecting to Google Cloud Agent Engine
 * Provides methods to query the deployed Workflow Analyzer Agent
 */

const AGENT_ENGINE_CONFIG = {
  projectId: 'dev-dispatch-478502-p8',
  location: 'global',
  agentId: '2664103479961714688', // Reasoning Engine ID from deployment
  endpoint: 'https://us-central1-aiplatform.googleapis.com/v1beta1',
};

/**
 * Query the deployed Agent Engine
 * @param {string} workflowText - The workflow text to analyze
 * @param {string} accessToken - Google OAuth access token
 * @returns {Promise<Object>} Analysis result from the agent
 */
export async function queryAgentEngine(workflowText, accessToken) {
  const url = `${AGENT_ENGINE_CONFIG.endpoint}/projects/${AGENT_ENGINE_CONFIG.projectId}/locations/${AGENT_ENGINE_CONFIG.location}/reasoningEngines/${AGENT_ENGINE_CONFIG.agentId}:streamQuery`;

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify({
        query: workflowText,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(
        `Agent Engine error: ${errorData.error?.message || response.statusText}`
      );
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error querying Agent Engine:', error);
    throw error;
  }
}

/**
 * Get access token via OAuth flow (requires Google Auth setup)
 * This is a placeholder - implement based on your auth method
 */
export function getAccessToken() {
  // If you're using Google Sign-In:
  // const user = gapi.auth2.getAuthInstance().currentUser.get();
  // return user.getAuthResponse().id_token;

  // Or retrieve from localStorage if stored during login
  return localStorage.getItem('googleAccessToken');
}

export const AGENT_ENGINE_CONFIG_EXPORT = AGENT_ENGINE_CONFIG;
