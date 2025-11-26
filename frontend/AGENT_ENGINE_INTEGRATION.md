# Connecting Frontend to Google Cloud Agent Engine

Your Workflow Analyzer agent is now deployed to Google Cloud's Agent Engine. This guide shows you how to connect your React frontend to the deployed agent.

## Deployment Details

- **Project ID:** `dev-dispatch-478502-p8`
- **Region:** `us-central1`
- **Agent Name:** `workflow-analyzer`
- **Reasoning Engine ID:** `2664103479961714688`
- **Location:** `global`

## Integration Approach

You have two main options:

### Option 1: Keep Local Backend (Recommended for now)

Your current setup uses a local Flask backend at `http://localhost:8000`. You can:
1. Keep your local backend running for all API calls
2. The backend orchestrates calls to the deployed Agent Engine
3. Pros: Simpler auth, caching, custom logic
4. Cons: Still need local backend running

**To do this:**
- Keep your current backend running: `python -m backend`
- No frontend changes needed
- Update backend to forward requests to Agent Engine (optional)

### Option 2: Direct Frontend to Agent Engine (Advanced)

Call Agent Engine directly from React frontend.

**Pros:**
- No local backend needed
- Direct cloud-to-cloud communication
- Real-time streaming responses

**Cons:**
- Requires Google OAuth authentication in frontend
- More complex CORS setup
- Need to handle auth tokens securely

## Option 1: Backend Proxy (Recommended)

Your local backend already works. To enhance it to use the deployed Agent Engine:

### Step 1: Update Backend Configuration

Edit `backend/deploy_config.py` to add the deployed Agent Engine endpoint:

```python
AGENT_ENGINE_ID = os.getenv("AGENT_ENGINE_ID", "2664103479961714688")
AGENT_ENGINE_LOCATION = os.getenv("AGENT_ENGINE_LOCATION", "global")
```

### Step 2: Create Backend Service for Agent Engine

Create `backend/services/agent_engine_client.py`:

```python
from google.cloud.aiplatform_v1 import ReasoningEngineServiceClient

class AgentEngineClient:
    def __init__(self, project_id, location, engine_id):
        self.client = ReasoningEngineServiceClient()
        self.project_id = project_id
        self.location = location
        self.engine_id = engine_id

    async def query(self, workflow_text):
        """Query the deployed reasoning engine"""
        name = f"projects/{self.project_id}/locations/{self.location}/reasoningEngines/{self.engine_id}"

        request = {
            "name": name,
            "input": {"query": workflow_text}
        }

        response = self.client.stream_query(request)
        return response
```

### Step 3: Update Your Orchestrator

Currently your backend uses `WorkflowAnalyzerOrchestrator` (local). To use the deployed agent:

**Option A: Hybrid** (Recommended)
- Keep orchestrator for local testing
- Add a feature flag to switch to Agent Engine in production

**Option B: Full Cloud**
- Replace local orchestrator with Agent Engine client
- Update endpoints to use cloud instance

## Option 2: Direct Frontend Integration (Advanced)

If you want to call Agent Engine directly from React:

### Step 1: Set Up Google Authentication

Install Google Auth library:
```bash
npm install @react-oauth/google google-auth-library-js-client
```

### Step 2: Wrap App with Google OAuth

In `frontend/src/index.js`:

```javascript
import { GoogleOAuthProvider } from '@react-oauth/google';

<GoogleOAuthProvider clientId="YOUR_GOOGLE_CLIENT_ID">
  <App />
</GoogleOAuthProvider>
```

### Step 3: Use Agent Engine Service

In `frontend/src/App.js`, update the `handleFileUpload` function:

```javascript
import { queryAgentEngine, getAccessToken } from './services/agentEngineService';

const handleFileUpload = async (file) => {
  setLoading(true);
  try {
    const workflowText = await file.text();
    const accessToken = getAccessToken();

    // Option: Call Agent Engine directly
    // const result = await queryAgentEngine(workflowText, accessToken);

    // Or: Keep calling local backend (current approach)
    const result = await fetchJsonWithRetry(
      WORKFLOW_API_BASE,
      { method: 'POST', ... }
    );

    setAnalysisResult(result);
  } catch (error) {
    setError(error.message);
  } finally {
    setLoading(false);
  }
};
```

## Testing the Connection

### Test 1: Verify Agent Engine is Running

```bash
python -c "
from google.cloud.aiplatform_v1 import ReasoningEngineServiceClient

client = ReasoningEngineServiceClient()
name = 'projects/dev-dispatch-478502-p8/locations/global/reasoningEngines/2664103479961714688'

# Try to get the engine
try:
    engine = client.get_reasoning_engine(name=name)
    print(f'Engine state: {engine.state}')
except Exception as e:
    print(f'Error: {e}')
"
```

### Test 2: Query Agent Engine from Backend

```python
from google.cloud.aiplatform_v1 import ReasoningEngineServiceClient

client = ReasoningEngineServiceClient()
name = 'projects/dev-dispatch-478502-p8/locations/global/reasoningEngines/2664103479961714688'

request = {
    'name': name,
    'input': {'query': 'Create user account and send email'}
}

response = client.stream_query(request)
for result in response:
    print(result)
```

### Test 3: Frontend Integration

```javascript
// In browser console
import { queryAgentEngine } from './services/agentEngineService';

const token = await getAccessToken();
const result = await queryAgentEngine('Create user account', token);
console.log(result);
```

## Architecture Options

### Architecture A: Local Backend + Cloud Agent Engine

```
Frontend (React)
    ↓
Local Backend (Flask)
    ↓
Cloud Agent Engine
```

**Setup:**
- Run: `python -m backend` locally
- Frontend calls: `http://localhost:8000/workflows`
- Backend calls: Cloud Agent Engine API

### Architecture B: Frontend + Cloud Agent Engine (No Local Backend)

```
Frontend (React) + OAuth
    ↓
Cloud Agent Engine
```

**Setup:**
- No local backend needed
- Frontend has Google OAuth token
- Direct API calls to Agent Engine

### Architecture C: Frontend + Local Orchestrator (Current)

```
Frontend (React)
    ↓
Local Backend (Flask)
    ↓
Local Orchestrator (Python)
```

**Setup:**
- Keep current setup
- Deploy later when needed

## Environment Variables

Add to your `.env` files:

**Frontend (.env):**
```
REACT_APP_GOOGLE_CLIENT_ID=your-client-id
REACT_APP_AGENT_ENGINE_ID=2664103479961714688
REACT_APP_GCP_PROJECT_ID=dev-dispatch-478502-p8
```

**Backend (.env):**
```
AGENT_ENGINE_ID=2664103479961714688
AGENT_ENGINE_LOCATION=global
```

## Recommended Next Steps

1. **Start with Option 1 (Backend Proxy)**
   - Less changes to frontend
   - Leverage existing API structure
   - Can add cloud agent alongside local one

2. **Test Backend → Agent Engine**
   - Create test endpoint
   - Verify auth and streaming works

3. **Update Frontend when ready**
   - Switch to Agent Engine calls
   - Update API endpoints
   - Test with real workflows

## Authentication Notes

- Agent Engine uses **Service Account** authentication via Google Cloud SDK
- Your local backend can use Application Default Credentials (ADC)
- Frontend requires OAuth 2.0 for direct calls
- Consider using a **service account key** for backend if not using ADC

## Troubleshooting

### Agent Engine returns "Permission denied"
- Ensure service account has `Vertex AI User` role
- Check `gcloud auth application-default login`

### CORS errors in frontend
- Agent Engine API has CORS restrictions
- Use backend proxy (Option 1) to avoid this
- Or configure CORS properly for frontend domain

### Auth token expiration
- Refresh tokens before expiry
- Implement token refresh logic in frontend

## Resources

- [Agent Engine Documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine)
- [Reasoning Engine API](https://cloud.google.com/vertex-ai/docs/generative-ai/reasoning-engine/overview)
- [Service Account Setup](https://cloud.google.com/docs/authentication/getting-started)
- [OAuth 2.0 for Web](https://developers.google.com/identity/protocols/oauth2)
