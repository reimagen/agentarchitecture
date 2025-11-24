# Firebase Setup Guide for AgentArchitecture

This guide walks you through setting up Firebase for the AgentArchitecture Workflow API.

## What Has Been Implemented

The following components are now ready to use:

### 1. **Firebase Client Module** (`backend/database/firebase_client.py`)
- Singleton pattern for Firebase Admin SDK initialization
- Automatic Firestore client creation
- Server timestamp management
- Credentials validation

### 2. **Workflow Repository** (`backend/database/workflow_repository.py`)
- CRUD operations for workflows
- Approval workflow management
- Org chart and registry persistence
- Auto-triggering of org design synthesis on approval
- List and query workflows with filtering

### 3. **REST API Endpoints**
- **Workflows API** (`backend/api/workflows.py`):
  - `POST /workflows` - Create and analyze workflow
  - `GET /workflows/{workflow_id}` - Retrieve workflow
  - `GET /workflows` - List workflows with filtering
  - `DELETE /workflows/{workflow_id}` - Delete workflow

- **Approval API** (`backend/api/approval.py`):
  - `POST /workflows/{workflow_id}/approve` - Approve workflow and trigger org design
  - `GET /workflows/{workflow_id}/approval-status` - Check approval status

### 4. **FastAPI Application** (`backend/api/app.py`)
- Ready-to-run FastAPI server
- CORS configured
- Firebase initialization on startup
- Health check and info endpoints

---

## Firebase Console Setup Instructions

### Step 1: Create/Access Firebase Project

1. Go to **[Firebase Console](https://console.firebase.google.com)**
2. Click **Create a project** (or select existing one)
3. Enter project name: `agentarchitecture` (or your preferred name)
4. Follow the setup wizard

### Step 2: Enable Firestore Database

1. In Firebase Console, navigate to **Firestore Database**
2. Click **Create database**
3. Choose **Production mode** (you can start with test mode if needed)
4. Select region: **us-central1** (recommended) or your preferred region
5. Click **Create**

### Step 3: Create Service Account & Download Credentials

1. Go to **Project Settings** (gear icon, top-right)
2. Navigate to **Service Accounts** tab
3. Click **Generate New Private Key**
4. A JSON file will download - this is your service account credentials
5. **Save this file as `backend/firebase-service-account.json`**
6. ⚠️ **IMPORTANT**: Add to `.gitignore` to prevent committing secrets

### Step 4: Update Environment Variables

Edit `backend/.env`:

```bash
# Firebase Configuration
FIREBASE_PROJECT_ID=your-project-id  # From Firebase Console
FIREBASE_CREDENTIALS_PATH=./firebase-service-account.json
FIREBASE_COLLECTION_WORKFLOWS=workflows
FIRESTORE_LOCATION=us-central1
```

Replace `your-project-id` with your actual Firebase Project ID (found in Project Settings).

### Step 5: Create Firestore Indexes (Optional for Phase 1)

For better performance with queries, create these indexes in Firestore Console:

1. **Workflows collection → Indexes tab**
2. Click **Create Index**
3. Create the following composite index:
   - **Collection**: `workflows`
   - **Fields**:
     - `approvalStatus` (Ascending)
     - `createdAt` (Descending)

Alternatively, Firestore will auto-suggest indexes when you run queries. You can approve them automatically.

### Step 6: Configure Firestore Security Rules

1. In Firestore Console, go to **Rules** tab
2. Replace with (Phase 1 - test mode):

```firestore-rules
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Allow all read/write in test mode (Phase 1 only)
    match /workflows/{workflow_id} {
      allow read, write: if true;
    }
  }
}
```

3. Click **Publish**

**Note**: After adding authentication, update these rules to enforce user-based access control.

---

## Running the FastAPI Application

### Prerequisites

1. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```

2. Ensure Firebase credentials are in place:
   - `backend/firebase-service-account.json` exists
   - `backend/.env` has correct `FIREBASE_CREDENTIALS_PATH`

### Start the API Server

#### Option 1: Using Python module
```bash
python -m backend.api.app
```

#### Option 2: Using uvicorn directly
```bash
uvicorn backend.api.app:app --reload --host 0.0.0.0 --port 8000
```

#### Option 3: Using the module entry point
```bash
python -c "from backend.api.app import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8000)"
```

### Verify API is Running

1. Open browser: **http://localhost:8000**
   - Should show API info

2. Check docs: **http://localhost:8000/docs**
   - Interactive API documentation (Swagger UI)

3. Health check: **http://localhost:8000/health**
   - Should return `{"status": "healthy"}`

---

## API Usage Examples

### 1. Analyze a Workflow

```bash
curl -X POST http://localhost:8000/workflows \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_text": "Step 1: Receive email\nStep 2: Process request\nStep 3: Send response"
  }'
```

Response:
```json
{
  "workflow_id": "wf_a1b2c3d4",
  "approvalStatus": "PENDING",
  "createdAt": "2025-11-18T20:10:00.000Z",
  "updatedAt": "2025-11-18T20:10:00.000Z",
  "analysis": { /* WorkflowAnalysis object */ }
}
```

### 2. Get Workflow Details

```bash
curl http://localhost:8000/workflows/wf_a1b2c3d4
```

### 3. List Pending Workflows

```bash
curl "http://localhost:8000/workflows?status=PENDING&limit=20"
```

### 4. Approve a Workflow (Triggers Org Design)

```bash
curl -X POST http://localhost:8000/workflows/wf_a1b2c3d4/approve \
  -H "Content-Type: application/json" \
  -d '{
    "approved_by": "generic_user",
    "notes": "Analysis looks good"
  }'
```

Response:
```json
{
  "workflow_id": "wf_a1b2c3d4",
  "approvalStatus": "APPROVED",
  "approvedBy": "generic_user",
  "approvedAt": "2025-11-18T20:30:00.000Z",
  "orgChart": { /* AgentOrgChart object */ },
  "agentRegistry": { /* Agent registry */ },
  "toolRegistry": { /* Tool registry */ },
  "updatedAt": "2025-11-18T20:31:00.000Z"
}
```

### 5. Check Approval Status

```bash
curl http://localhost:8000/workflows/wf_a1b2c3d4/approval-status
```

### 6. Delete a Workflow

```bash
curl -X DELETE http://localhost:8000/workflows/wf_a1b2c3d4
```

---

## Data Flow

### Analysis Flow
```
1. POST /workflows
   ↓
2. Orchestrator.analyze_workflow()
   ├─ Parse workflow into steps
   ├─ Assess risks
   ├─ Analyze automation potential
   ├─ Auto-save to Firestore (status: PENDING)
   └─ Return analysis
3. Response to user
```

### Approval & Org Design Flow
```
1. POST /workflows/{id}/approve
   ↓
2. WorkflowRepository.approve_workflow()
   ├─ Update status to APPROVED in Firestore
   ├─ Trigger org_design_service.run_org_design_for_analysis()
   │  ├─ Generate org chart from analysis
   │  ├─ Create agent registry
   │  ├─ Create tool registry
   │  └─ Save all to Firestore
   └─ Return updated workflow with org chart
3. Response to user
```

---

## Firestore Data Structure

### Collections

```
firestore/
└── workflows/
    ├── wf_a1b2c3d4/
    │   ├── originalText: string
    │   ├── analysis: object (WorkflowAnalysis)
    │   ├── orgChart: object (AgentOrgChart) [null until approved]
    │   ├── agentRegistry: object
    │   ├── toolRegistry: object
    │   ├── approvalStatus: "PENDING" | "APPROVED" | "REJECTED"
    │   ├── approvedBy: string | null
    │   ├── approvedAt: timestamp | null
    │   ├── createdBy: string
    │   ├── createdAt: timestamp
    │   ├── updatedAt: timestamp
    │   ├── sessionId: string
    │   └── metadata: object
    │
    └── ... (more workflows)
```

---

## Environment Variables Reference

```bash
# Existing
GEMINI_AI_API=your-api-key

# Firebase Configuration (add these)
FIREBASE_PROJECT_ID=agentarchitecture-xxxxx
FIREBASE_CREDENTIALS_PATH=./firebase-service-account.json
FIREBASE_COLLECTION_WORKFLOWS=workflows
FIRESTORE_LOCATION=us-central1
```

---

## Troubleshooting

### Firebase Not Initialized
**Error**: `"Firebase not initialized. Call FirebaseClient.initialize() first."`

**Solution**:
1. Verify `firebase-service-account.json` exists in `backend/` directory
2. Check `FIREBASE_CREDENTIALS_PATH` in `.env`
3. Ensure file path is correct (absolute or relative to working directory)

### Credentials File Not Found
**Error**: `FileNotFoundError: Firebase credentials file not found`

**Solution**:
1. Download service account JSON from Firebase Console
2. Save as `backend/firebase-service-account.json`
3. Verify file permissions (should be readable)

### Permission Denied on Firestore
**Error**: `PERMISSION_DENIED: Permission denied on resource`

**Solution**:
1. Verify Firestore Security Rules are set to allow read/write
2. Check service account has `roles/datastore.user` permission
3. For production, configure proper security rules

### Workflow Not Saving to Firestore
**Check**:
1. API logs show "Failed to persist analysis to Firestore"
2. Verify Firestore database exists and is accessible
3. Check Firebase credentials are valid
4. Ensure `FIREBASE_COLLECTION_WORKFLOWS` matches your collection name

### Import Errors
**Error**: `ModuleNotFoundError: No module named 'firebase_admin'`

**Solution**:
```bash
pip install -r backend/requirements.txt
```

---

## File Structure

```
backend/
├── api/
│   ├── __init__.py
│   ├── app.py                 # FastAPI application
│   ├── workflows.py           # Workflow CRUD endpoints
│   └── approval.py            # Approval workflow endpoints
│
├── database/
│   ├── __init__.py
│   ├── database-plan.md       # Architecture documentation
│   ├── exceptions.py          # Custom exception classes
│   ├── firebase_client.py     # Firebase initialization
│   └── workflow_repository.py # Firestore repository
│
├── agent/
│   ├── workflow_analyzer_agent/
│   │   ├── orchestrator.py    # Modified: auto-save analysis
│   │   └── ...
│   └── ...
│
├── .env                        # Environment variables (modified)
├── requirements.txt            # Dependencies (modified)
├── firebase-service-account.json  # Credentials (add this, gitignored)
└── ...
```

---

## Next Steps

1. ✅ Implement Firebase initialization and Firestore repository
2. ✅ Create REST API endpoints
3. ✅ Set up FastAPI application
4. **TODO**: Create Firestore security rules and indexes (in Firebase Console)
5. **TODO**: Test API endpoints end-to-end
6. **TODO**: Add authentication (Phase 2)
7. **TODO**: Deploy to Google Cloud (Phase 3)

---

## Support

For issues or questions:
1. Check Firestore logs: **Firebase Console → Logs**
2. Review API server output for errors
3. Verify environment variables: `echo $FIREBASE_PROJECT_ID`
4. Test Firebase connectivity with simple script (provided below)

### Test Firebase Connectivity

```python
# test_firebase.py
import os
from dotenv import load_dotenv
from backend.database.firebase_client import FirebaseClient

load_dotenv()

try:
    FirebaseClient.initialize()
    db = FirebaseClient.get_db()
    print("✓ Firebase connected successfully")

    # Test write
    db.collection("workflows").document("test").set({"test": True})
    print("✓ Successfully wrote to Firestore")

    # Test read
    doc = db.collection("workflows").document("test").get()
    print(f"✓ Successfully read from Firestore: {doc.to_dict()}")

except Exception as e:
    print(f"✗ Firebase connection failed: {e}")
```

Run with:
```bash
python test_firebase.py
```

---

## Firebase Console Links

Replace `PROJECT_ID` with your Firebase project ID:

- **Dashboard**: https://console.firebase.google.com/project/PROJECT_ID
- **Firestore**: https://console.firebase.google.com/project/PROJECT_ID/firestore
- **Settings**: https://console.firebase.google.com/project/PROJECT_ID/settings/general
- **Service Accounts**: https://console.firebase.google.com/project/PROJECT_ID/settings/serviceaccounts
