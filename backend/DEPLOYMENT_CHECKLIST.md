# Deployment Checklist

Use this checklist to track your deployment progress.

## Pre-Deployment (Do Now)

- [x] Python 3.13.9 verified
- [x] Vertex AI SDK (1.128.0) installed
- [x] Deployment configuration files created
- [ ] **Google Cloud SDK installed** (requires manual download/install)
  - Download from: https://cloud.google.com/sdk/docs/install#windows
  - After install, restart terminal and run: `gcloud --version`

## Configuration Setup

- [ ] Copy `.env.example` to `.env`
  ```bash
  cp .env.example .env
  ```

- [ ] Update `.env` with your values:
  ```
  GCP_PROJECT_ID=your-project-id
  GCP_LOCATION=us-central1
  GCS_STAGING_BUCKET=gs://your-bucket-name
  GOOGLE_API_KEY=your-api-key
  FIREBASE_PROJECT_ID=your-firebase-project
  FIREBASE_CREDENTIALS_PATH=./firebase-service-account.json
  ```

## Google Cloud Setup

- [ ] Authenticate gcloud:
  ```bash
  gcloud auth application-default login
  ```

- [ ] Set project ID:
  ```bash
  gcloud config set project YOUR_PROJECT_ID
  ```

- [ ] Enable Vertex AI API in Google Cloud Console
  - Link: https://console.cloud.google.com/apis/library/aiplatform.googleapis.com

- [ ] Create staging bucket:
  ```bash
  gsutil mb gs://your-staging-bucket-name
  ```

## Pre-Deployment Testing

- [ ] Test orchestrator locally:
  ```bash
  python -m backend --workflow "Sample workflow"
  ```

- [ ] Verify Firebase connectivity
  - Check `.env` has correct credentials path
  - Confirm Firebase service account JSON exists

- [ ] Verify Google API key works
  - Run: `python -c "from agent.workflow_analyzer_agent.orchestrator import WorkflowAnalyzerOrchestrator; print('OK')"`

## Deployment

- [ ] Review `agent_engine_app.py` - Agent Engine wrapper
- [ ] Review `deploy_config.py` - Configuration management
- [ ] Ensure all environment variables are set in `.env`

**Choose deployment method:**

- [ ] **Option A: Agent Starter Pack** (Recommended)
  ```bash
  uvx agent-starter-pack enhance --adk -d agent_engine
  make backend
  ```

- [ ] **Option B: ADK CLI**
  ```bash
  adk deploy agent_engine \
    --app backend.agent_engine_app:app \
    --name workflow-analyzer \
    --description "Multi-agent workflow analysis system" \
    --location us-central1
  ```

## Post-Deployment Verification

- [ ] Check deployment status:
  ```bash
  adk get agent_engine workflow-analyzer
  ```

- [ ] Verify in Agent Engine UI:
  - https://console.cloud.google.com/vertex-ai/agent-engine

- [ ] Test via Python SDK:
  ```python
  from google.cloud import aiplatform
  aiplatform.init(project="YOUR_PROJECT_ID", location="us-central1")
  app = aiplatform.Agent.list(filter="display_name=workflow-analyzer")[0]
  response = app.query(input_text="Test workflow")
  print(response)
  ```

- [ ] Test via REST API (use `gcloud auth print-access-token` for auth)

## Monitoring & Operations

- [ ] Set up Cloud Logging
  - https://console.cloud.google.com/logs

- [ ] Set up Cloud Monitoring
  - https://console.cloud.google.com/monitoring

- [ ] Create alerts for:
  - Agent Engine errors
  - High latency (>30s)
  - Failed workflow analyses

## Rollback/Cleanup

- [ ] Test deletion (if needed):
  ```bash
  adk delete agent_engine workflow-analyzer
  ```

- [ ] Keep .env.example updated with new variables
- [ ] Document any manual steps taken

## Final Sign-Off

- [ ] All tests passing locally
- [ ] Deployed successfully to Agent Engine
- [ ] Verified in UI and via API
- [ ] Monitoring setup complete
- [ ] Team notified of deployment

---

**Notes:**
- Keep Firebase service account credentials secure (in `.gitignore`)
- Don't commit `.env` file with real values
- Monitor costs in Google Cloud Console
- Use staging environment first if available
