# Agent Engine Deployment Guide

This guide walks you through deploying the Workflow Analyzer to Google Cloud's Agent Engine.

## Prerequisites

- [ ] Python 3.9-3.13 (confirmed: 3.13.9)
- [ ] Google Cloud SDK (`gcloud` CLI)
- [ ] Google Cloud Project with billing enabled
- [ ] Vertex AI API enabled in your project
- [ ] Google Cloud Storage bucket for staging

## Setup Steps

### Step 1: Install Google Cloud SDK

**Windows:**
1. Download from: https://cloud.google.com/sdk/docs/install#windows
2. Run the `.msi` installer
3. Follow the setup wizard
4. Restart your terminal
5. Verify: `gcloud --version`

**After Installation:**
```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

### Step 2: Environment Configuration

Copy the example environment file and update with your values:

```bash
cp .env.example .env
```

Edit `.env` with your values:
```
GCP_PROJECT_ID=your-google-cloud-project-id
GCP_LOCATION=us-central1
GCS_STAGING_BUCKET=gs://your-staging-bucket-name
GOOGLE_API_KEY=your-google-api-key
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_CREDENTIALS_PATH=./firebase-service-account.json
```

### Step 3: Create GCS Staging Bucket

The staging bucket is required by Agent Engine to upload your agent code.

```bash
gsutil mb gs://your-staging-bucket-name
```

Or create via Google Cloud Console:
1. Go to Cloud Storage
2. Click "Create Bucket"
3. Name: `your-staging-bucket-name`
4. Location: Same region as deployment (e.g., `us-central1`)

### Step 4: Verify Local Setup

Test the agent locally before deploying:

```bash
python -m backend --workflow "Example workflow text"
```

Or test via Python:
```python
import asyncio
from agent.workflow_analyzer_agent.orchestrator import WorkflowAnalyzerOrchestrator

async def test():
    orchestrator = WorkflowAnalyzerOrchestrator()
    result = await orchestrator.analyze_workflow("Your workflow text here")
    print(result)

asyncio.run(test())
```

### Step 5: Deploy to Agent Engine

**Option A: Using Agent Starter Pack (Recommended)**

```bash
uvx agent-starter-pack enhance --adk -d agent_engine
make backend
```

**Option B: Using ADK CLI**

```bash
adk deploy agent_engine \
  --app backend.agent_engine_app:app \
  --name workflow-analyzer \
  --description "Multi-agent workflow analysis system" \
  --location us-central1
```

### Step 6: Verify Deployment

1. Check deployment status:
```bash
adk get agent_engine workflow-analyzer
```

2. View in Agent Engine UI:
   - Go to: https://console.cloud.google.com/vertex-ai/agent-engine
   - Look for "workflow-analyzer"

### Step 7: Test Deployed Agent

**Via Python SDK:**
```python
from google.cloud import aiplatform

# Initialize Vertex AI
aiplatform.init(project="YOUR_PROJECT_ID", location="us-central1")

# Get your deployed agent
app = aiplatform.Agent.list(filter="display_name=workflow-analyzer")[0]

# Test with a query
response = app.query(input_text="Your workflow text here")
print(response)
```

**Via REST API:**
```bash
curl -X POST \
  https://us-central1-aiplatform.googleapis.com/v1/projects/YOUR_PROJECT_ID/locations/us-central1/agentEngines \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Your workflow text here"
  }'
```

## Files Created for Deployment

- **`agent_engine_app.py`** - Agent Engine wrapper and entry point
- **`deploy_config.py`** - Deployment configuration management
- **`.env.example`** - Environment variable template
- **`DEPLOYMENT_GUIDE.md`** - This file

## Configuration Files

### `deploy_config.py`

Centralized deployment configuration. Update values here or via environment variables:

```python
from deploy_config import DeploymentConfig

# Use configuration
print(DeploymentConfig.PROJECT_ID)
print(DeploymentConfig.STAGING_BUCKET)
```

## Troubleshooting

### Issue: "gcloud command not found"
- Install Google Cloud SDK: https://cloud.google.com/sdk/docs/install
- Add to PATH if not done automatically
- Restart terminal after installation

### Issue: "GCP_PROJECT_ID not set"
- Create `.env` file from `.env.example`
- Set `GCP_PROJECT_ID` to your Google Cloud Project ID
- Run: `gcloud config set project YOUR_PROJECT_ID`

### Issue: "Staging bucket not found"
- Create the bucket: `gsutil mb gs://bucket-name`
- Ensure bucket name matches `GCS_STAGING_BUCKET` in `.env`

### Issue: "Vertex AI API not enabled"
- Enable in Google Cloud Console:
  - Go to APIs & Services → Library
  - Search for "Vertex AI API"
  - Click "Enable"

### Issue: "Firebase credentials not found"
- Download service account JSON from Firebase Console
- Save to path specified in `FIREBASE_CREDENTIALS_PATH`
- Ensure file is in `.gitignore` (security)

## Architecture Overview

```
┌─────────────────────────────────────────┐
│     Agent Engine (Google Cloud)         │
└──────────────┬──────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────┐
│   agent_engine_app.py (AdkApp wrapper)  │
└──────────────┬──────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────┐
│   WorkflowAnalyzerOrchestrator          │
│   ├─ Agent 1: WorkflowParser            │
│   ├─ Agent 2: RiskAssessor              │
│   ├─ Agent 3: AutomationAnalyzer        │
│   └─ Agent 4: AutomationSummarizer      │
└──────────────┬──────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────┐
│   External Services                     │
│   ├─ Google Generative AI (Gemini)      │
│   ├─ Firestore                          │
│   └─ Google Cloud Storage               │
└─────────────────────────────────────────┘
```

## Next Steps

1. ✅ Install Google Cloud SDK
2. ✅ Configure environment variables
3. ✅ Create staging bucket
4. ✅ Test locally
5. ✅ Deploy to Agent Engine
6. ✅ Monitor in UI
7. ✅ Set up monitoring/alerts

## References

- [Agent Engine Documentation](https://google.github.io/adk-docs/deploy/agent-engine/)
- [Google Cloud SDK Installation](https://cloud.google.com/sdk/docs/install)
- [Vertex AI Agent Framework](https://cloud.google.com/python/docs/reference/aiplatform/latest)
- [ADK Documentation](https://google.github.io/adk-docs/)
