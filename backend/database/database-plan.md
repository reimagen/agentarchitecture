# Database Architecture Plan: Firebase Integration

## Executive Summary

This plan introduces persistent storage for workflow artifacts using **Firebase Firestore** as the primary database. Firebase was chosen because:
- Already in the Google environment (leverages existing Google Cloud infrastructure)
- Native integration with Google Generative AI (google-genai already in use)
- Serverless, auto-scaling architecture (no ops overhead)
- Built-in authentication and security rules
- Real-time capabilities for future multi-user workflows
- JSON-document model aligns perfectly with our data structures (WorkflowAnalysis, AgentOrgChart)

---

## Data Model Architecture

### Firestore Collection Structure

```
firestore/
└── workflows/                           # Main workflows collection
    ├── {workflow_id}/                  # Document: workflow record
    │   ├── originalText: string        # Raw workflow text input
    │   ├── analysis: object            # WorkflowAnalysis JSON
    │   ├── orgChart: object            # AgentOrgChart JSON (null until approved & synthesized)
    │   ├── agentRegistry: object       # Agent registry dict (null until synthesis)
    │   ├── toolRegistry: object        # Tool registry dict (null until synthesis)
    │   ├── approvalStatus: string      # PENDING | APPROVED | REJECTED
    │   ├── approvedBy: string          # User ID who approved (null if PENDING, e.g. "generic_user")
    │   ├── approvedAt: timestamp       # When approved (null if PENDING)
    │   ├── createdBy: string           # User ID who created workflow (e.g. "generic_user")
    │   ├── createdAt: timestamp        # When first stored
    │   ├── updatedAt: timestamp        # Last modification
    │   ├── sessionId: string           # Reference to analysis session
    │   └── metadata: object            # User notes, tags, custom fields
    │
    └── ... (more workflow documents)
```

**Note:** Firebase Authentication not implemented in Phase 1. Using generic user identifier ("generic_user") for createdBy and approvedBy fields.

### Document Schema Details

#### `workflows/{workflow_id}` Document

| Field | Type | Description | Required | Example |
|-------|------|-------------|----------|---------|
| `originalText` | string | Raw workflow text submitted by user | Yes | "Customer receives email..." |
| `analysis` | object | Complete WorkflowAnalysis JSON from orchestrator | Yes | `{workflow_id, steps: [...], summary: {...}, ...}` |
| `orgChart` | object | AgentOrgChart JSON from synthesis (null until approved and synthesized) | No | `{workflow_id, agents: [...], connections: [...]}` |
| `agentRegistry` | object | Agent registry (dict of agents keyed by agent_id) - persisted separately | No | `{agent_step_1: {...}, agent_step_2: {...}}` |
| `toolRegistry` | object | Tool registry (dict of tools keyed by tool_id) - persisted separately | No | `{tool_1: {...}, tool_2: {...}}` |
| `approvalStatus` | string | Enum: PENDING \| APPROVED \| REJECTED | Yes | "PENDING" |
| `approvedBy` | string | User identifier (generic user or future user_id) | No | "generic_user" |
| `approvedAt` | timestamp | ISO 8601 timestamp of approval | No | "2025-11-18T20:30:00Z" |
| `createdBy` | string | User identifier who submitted workflow (generic user or future user_id) | Yes | "generic_user" |
| `createdAt` | timestamp | When workflow first stored | Yes | "2025-11-18T20:10:00Z" |
| `updatedAt` | timestamp | Last modification timestamp | Yes | "2025-11-18T20:10:00Z" |
| `sessionId` | string | Reference to analysis session UUID | Yes | "2232bc88-f1c6-487c-91ca-1c76b8c80e2f" |
| `metadata` | object | Freeform metadata (user notes, tags, etc.) | No | `{notes: "...", tags: ["urgent"], version: 1}` |

**Indexes Required:**
- `approvalStatus` (for filtering workflows by status)
- `createdAt` (for sorting by creation date)
- Composite: `(approvalStatus, updatedAt)` (for "pending workflows, newest first")

#### Example Document Instance

```json
{
  "originalText": "Customer support workflow...",
  "analysis": {
    "workflow_id": "wf_2232bc88",
    "session_id": "2232bc88-f1c6-487c-91ca-1c76b8c80e2f",
    "steps": [
      {
        "id": "step_1",
        "description": "Receive customer email from inbox",
        "inputs": ["customer email"],
        "outputs": ["email received"],
        "dependencies": [],
        "agent_type": "TOOL",
        "risk_level": "UNKNOWN",
        "requires_human_review": false,
        "determinism_score": 1.0,
        "automation_feasibility": 1.0,
        "available_api": "Gmail API",
        "suggested_tools": ["Gmail API"],
        "mitigation_suggestions": [],
        "implementation_notes": "Use filters to target specific customer emails."
      }
      // ... 7 more steps
    ],
    "summary": {
      "total_steps": 8,
      "automatable_count": 7,
      "agent_required_count": 7,
      "human_required_count": 1,
      "automation_potential": 0.875
    },
    "key_insights": ["Prioritize automation of 7 automatable steps", "..."],
    "recommendations": ["..."],
    "analysis_timestamp": "2025-11-18T19:43:38.514079",
    "analysis_duration_ms": 55520.57820840454
  },
  "orgChart": null,
  "agentRegistry": null,
  "toolRegistry": null,
  "approvalStatus": "PENDING",
  "approvedBy": null,
  "approvedAt": null,
  "createdBy": "generic_user",
  "createdAt": "2025-11-18T20:10:00.000Z",
  "updatedAt": "2025-11-18T20:10:00.000Z",
  "sessionId": "2232bc88-f1c6-487c-91ca-1c76b8c80e2f",
  "metadata": {
    "notes": "Initial analysis",
    "tags": [],
    "version": 1
  }
}
```

#### After Approval (Updated Document)

```json
{
  "originalText": "Customer support workflow...",
  "analysis": { /* same as above */ },
  "orgChart": {
    "workflow_id": "wf_2232bc88",
    "agents": [
      {
        "id": "agent_step_1",
        "name": "Agent for step_1",
        "description": "Receive customer email from inbox",
        "mode": "TOOL_ONLY",
        "capabilities": [],
        "data_domains": [],
        "step_ids": ["step_1"],
        "tool_ids": ["api::Gmail API", "tool::Gmail API"],
        "input_schema": {"inputs": ["customer email"]},
        "output_schema": {"outputs": ["email received"]},
        "safety_constraints": {
          "requires_human_approval": false,
          "restricts_pii": false
        },
        "metadata": {
          "agent_type": "TOOL",
          "risk_level": "UNKNOWN",
          "automation_feasibility": 1.0
        }
      }
      // ... 7 more agents
    ],
    "connections": [
      {
        "from_agent_id": "agent_step_1",
        "to_agent_id": "agent_step_2",
        "description": "Output of step_1 feeds into step_2",
        "payload_schema": {"type": "workflow_step_output"},
        "channel": "request_response"
      }
      // ... 9 more connections
    ],
    "created_from_analysis_id": "2232bc88-f1c6-487c-91ca-1c76b8c80e2f",
    "metadata": {
      "total_agents": 8,
      "total_connections": 10
    }
  },
  "agentRegistry": {
    "agent_step_1": { /* agent card object */ },
    "agent_step_2": { /* agent card object */ },
    // ... 6 more agents
  },
  "toolRegistry": {
    "api::Gmail API": { /* tool details */ },
    "tool::Gmail API": { /* tool details */ },
    // ... more tools
  },
  "approvalStatus": "APPROVED",
  "approvedBy": "generic_user",
  "approvedAt": "2025-11-18T20:30:00.000Z",
  "createdBy": "generic_user",
  "createdAt": "2025-11-18T20:10:00.000Z",
  "updatedAt": "2025-11-18T20:31:00.000Z",
  "sessionId": "2232bc88-f1c6-487c-91ca-1c76b8c80e2f",
  "metadata": {
    "notes": "Initial analysis",
    "tags": ["approved"],
    "version": 1
  }
}
```

---

## Phase-by-Phase Implementation

### PHASE 1: Firebase Project & Client Setup

#### Step 1.1 - Firebase Project Configuration
1. Ensure Firebase project exists in Google Cloud console
2. Enable Firestore database:
   - Region: `us-central1` (or appropriate region)
   - Start in test mode (initially), transition to production rules
3. **Note:** Firebase Authentication will NOT be set up in Phase 1 (no user accounts needed yet)
4. Note Firebase config values:
   - Project ID
   - API Key
   - Storage bucket (for future file uploads if needed)

#### Step 1.2 - Add Firebase Dependencies
**File to modify:** `backend/requirements.txt`

```
firebase-admin>=6.5.0
google-cloud-firestore>=2.15.0
google-cloud-core>=2.4.0
python-dateutil>=2.8.2
```

**Rationale:**
- `firebase-admin`: Official Firebase Admin SDK for Python
- `google-cloud-firestore`: Low-level Firestore client
- `python-dateutil`: For robust timestamp handling

#### Step 1.3 - Create Firebase Initialization Module
**New file:** `backend/database/firebase_client.py`

**Responsibilities:**
- Initialize Firebase Admin SDK using service account credentials
- Create Firestore client instance
- Provide singleton pattern to avoid multiple initializations
- Handle initialization errors gracefully

**Key Code Structure (pseudocode):**
```python
class FirebaseClient:
    _instance = None

    @classmethod
    def initialize(cls, credentials_path: str):
        # Load service account JSON from Google Cloud
        # Initialize Firebase Admin SDK
        # Return client instance

    @classmethod
    def get_db(cls) -> firestore.Client:
        # Return Firestore client

    @classmethod
    def get_timestamp(cls) -> Timestamp:
        # Wrapper for consistent server-side timestamps
```

#### Step 1.4 - Environment Configuration
**File to modify:** `backend/.env` (already exists in backend/)

Add the following Firebase configuration variables:

```
# Firebase Configuration
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_CREDENTIALS_PATH=./firebase-service-account.json
FIREBASE_COLLECTION_WORKFLOWS=workflows
FIRESTORE_LOCATION=us-central1
```

**Note:** `firebase-service-account.json` should NOT be committed to git. Add to `.gitignore` in project root.

---

### PHASE 2: Create Firestore Repository Service

#### Step 2.1 - Build WorkflowRepository for Firestore
**New file:** `backend/database/workflow_repository.py`

**Class: WorkflowRepository**

**Method: `save_workflow_analysis(workflow_id: str, original_text: str, analysis: WorkflowAnalysis) -> None`**
- Creates or updates workflow document in `workflows/{workflow_id}`
- Fields set:
  - `originalText`: original_text
  - `analysis`: analysis.dict() (serialize Pydantic model to JSON)
  - `approvalStatus`: "PENDING"
  - `approvedBy`: None
  - `approvedAt`: None
  - `createdAt`: server timestamp (if new doc) or existing value
  - `updatedAt`: server timestamp
  - `sessionId`: analysis.session_id
  - `metadata`: {notes: "", tags: [], version: 1}
  - `orgChart`: None
- Error handling: Catch Firestore exceptions (quota, permissions, etc.)

**Method: `get_workflow_analysis(workflow_id: str) -> Optional[WorkflowAnalysis]`**
- Retrieves `workflows/{workflow_id}` document
- Extracts `analysis` field
- Deserializes from dict back to WorkflowAnalysis Pydantic model
- Returns None if not found

**Method: `approve_workflow(workflow_id: str, approved_by: str) -> Dict[str, Any]`**
- Preconditions:
  - Document must exist
  - approvalStatus must be "PENDING" (validate before update)
- Fields updated:
  - `approvalStatus`: "APPROVED"
  - `approvedBy`: approved_by
  - `approvedAt`: server timestamp
  - `updatedAt`: server timestamp
- Error handling:
  - Raise `WorkflowNotFoundError` if doc missing
  - Raise `InvalidApprovalStateError` if already approved/rejected
- Returns: Updated document dict

**Method: `get_approval_status(workflow_id: str) -> Optional[str]`**
- Retrieves only `approvalStatus` field from document
- Returns: "PENDING" | "APPROVED" | "REJECTED" | None if not found
- Optimization: Use field mask to reduce bandwidth

**Method: `save_org_chart(workflow_id: str, org_chart: AgentOrgChart, agent_registry: Dict, tool_registry: Dict) -> None`**
- Updates `workflows/{workflow_id}` document
- Fields set:
  - `orgChart`: org_chart.dict() (serialize to JSON)
  - `agentRegistry`: agent_registry (persist separately for easier querying)
  - `toolRegistry`: tool_registry (persist separately for easier querying)
  - `updatedAt`: server timestamp
- Precondition: Validate document exists (don't create new)
- Error handling: Catch Firestore exceptions
- Note: Registries stored separately for independent access and querying

**Method: `get_org_chart(workflow_id: str) -> Optional[AgentOrgChart]`**
- Retrieves `orgChart` field from `workflows/{workflow_id}`
- Deserializes from dict back to AgentOrgChart Pydantic model
- Returns None if not found or if orgChart is null

**Method: `list_workflows(approval_status: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]`**
- Query `workflows` collection
- If status provided: filter by `approvalStatus == status`
- Order by: `createdAt` descending (newest first)
- Limit results: default 50
- Return lightweight metadata only (workflow_id, approvalStatus, createdAt, updatedAt)
- Support pagination: return cursor for next page if results > limit

**Method: `delete_workflow(workflow_id: str) -> bool`**
- Soft or hard delete based on requirements
- Hard delete: Remove document entirely
- Soft delete: Set a `deletedAt` timestamp, exclude from normal queries
- Recommendation: Soft delete for audit trail

**Error Handling:**
```
WorkflowNotFoundError: Document doesn't exist
InvalidApprovalStateError: Workflow in wrong state for operation
FirestoreError: Low-level Firestore exception (quota, permissions, etc.)
SerializationError: Pydantic model serialization/deserialization failed
```

---

### PHASE 3: Firestore Security & Indexing

#### Step 3.1 - Configure Firestore Security Rules
**File:** `backend/database/firestore.rules` (deploy via Firebase CLI)

**Phase 1 Rules (No Authentication):**
Since Firebase Authentication is not implemented in Phase 1, use permissive test rules:

```
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

**Future Rules (Post-Auth):**
When Firebase Authentication is added:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Workflows collection rules
    match /workflows/{workflow_id} {
      // Authenticated users can read their own workflows
      allow read: if request.auth != null &&
                     request.auth.uid == resource.data.createdBy;

      // Authenticated users can create new workflows
      allow create: if request.auth != null &&
                       request.resource.data.createdBy == request.auth.uid;

      // Users can update (approve) their own workflows
      allow update: if request.auth != null &&
                       (resource.data.createdBy == request.auth.uid ||
                        request.auth.token.admin == true);
    }
  }
}
```

#### Step 3.2 - Create Firestore Indexes
**Firestore Index Definitions:**

| Collection | Fields | Type |
|-----------|--------|------|
| `workflows` | `approvalStatus` | Single field |
| `workflows` | `createdAt` | Single field (descending) |
| `workflows` | `(approvalStatus, updatedAt)` | Composite |

**Deployment:**
- Create indexes via Firebase Console (Firestore → Indexes tab)
- OR deploy via `firestore.indexes.json` (recommended for IaC)

```json
{
  "indexes": [
    {
      "collectionGroup": "workflows",
      "queryScope": "Collection",
      "fields": [
        {
          "fieldPath": "approvalStatus",
          "order": "ASCENDING"
        },
        {
          "fieldPath": "createdAt",
          "order": "DESCENDING"
        }
      ]
    }
  ]
}
```

---

### PHASE 4: Wire Approval Path into Orchestrator

#### Step 4.1 - Modify Orchestrator to Auto-Save Analysis
**File to modify:** `backend/agent/workflow_analyzer_agent/orchestrator.py`

**Location:** In `analyze_workflow()` method, after `_merge_results()` completes

**Changes:**
1. Inject `WorkflowRepository` dependency (via constructor or parameter)
2. After WorkflowAnalysis object is created:
   ```python
   # Save to Firestore immediately after analysis
   self.workflow_repository.save_workflow_analysis(
       workflow_id=analysis.workflow_id,
       original_text=workflow_text,
       analysis=analysis
   )
   ```
3. Return analysis as before
4. Error handling: Log exceptions but don't block analysis completion
   - If save fails, analysis still succeeds (fail-open for UX)
   - Add warning log: "Analysis saved successfully" or "Warning: failed to persist analysis"

**Rationale:**
- Ensures every completed analysis is persisted automatically
- No data loss even if approval flow never happens
- Minimal changes to existing code (add 3-4 lines)

#### Step 4.2 - Modify org_design/service.py to Enforce Approval
**File to modify:** `backend/agent/org_design/service.py`

**Function: `run_org_design_for_analysis()`**

**Changes:**
1. Add parameter: `workflow_repository: WorkflowRepository`
2. Add validation step at function start:
   ```python
   approval_status = workflow_repository.get_approval_status(analysis.workflow_id)
   if approval_status != "APPROVED":
       raise ApprovalRequiredException(
           f"Workflow {analysis.workflow_id} is not approved. "
           f"Current status: {approval_status}. "
           f"Approval required before org design synthesis."
       )
   ```
3. After org chart synthesis completes:
   ```python
   # Persist org chart and registries to Firestore
   workflow_repository.save_org_chart(
       workflow_id=analysis.workflow_id,
       org_chart=org_chart,
       agent_registry=agent_registry,
       tool_registry=tool_registry
   )
   ```
4. Return org_chart, agent_registry, tool_registry as before
5. Create custom exception class: `ApprovalRequiredException(Exception)`

**Rationale:**
- Enforcement gate: org design only proceeds for approved workflows
- Automatic persistence: results saved to Firestore immediately
- Audit trail: ties org chart back to original analysis via workflow_id

#### Step 4.3 - Auto-Trigger Org Design on Approval
**File to modify:** `backend/database/workflow_repository.py` (in `approve_workflow()` method)

**Changes:**
1. After setting approval status to "APPROVED" in Firestore
2. Immediately trigger org design synthesis:
   ```python
   # After approval is recorded in Firestore
   from backend.agent.org_design.service import run_org_design_for_analysis

   # Retrieve analysis
   analysis = self.get_workflow_analysis(workflow_id)

   # Run org design (now that approval status == APPROVED)
   org_chart, agent_registry, tool_registry = run_org_design_for_analysis(
       analysis=analysis,
       workflow_repository=self
   )
   # org chart auto-saves inside run_org_design_for_analysis()
   ```
3. Error handling: Log synthesis errors but approval still succeeds
   - Approval persisted regardless of synthesis success/failure
   - Add warning log if synthesis fails

**Rationale:**
- Synthesis automatically happens after approval (no separate API call needed)
- Seamless user experience: approve → immediately see org chart
- Synthesis failure doesn't rollback approval (fail-forward)

---

### PHASE 5: Create REST API Endpoints (FastAPI)

#### Step 5.1 - Workflow CRUD Endpoints
**New file:** `backend/api/workflows.py`

**Endpoint: `POST /workflows`**
```
Request:
{
  "workflow_text": "customer support workflow...",
  "workflow_id": "optional_uuid_or_leave_null"
}

Processing:
1. If no workflow_id: generate one (uuid.uuid4() or hash of text)
2. Call orchestrator.analyze_workflow(workflow_text)
3. (Auto-save happens in orchestrator)
4. Retrieve saved workflow from Firestore

Response:
{
  "workflow_id": "wf_2232bc88",
  "approvalStatus": "PENDING",
  "createdAt": "2025-11-18T20:10:00.000Z",
  "updatedAt": "2025-11-18T20:10:00.000Z",
  "analysis": { /* WorkflowAnalysis JSON */ }
}

HTTP Status: 201 Created
```

**Endpoint: `GET /workflows/{workflow_id}`**
```
Processing:
1. Retrieve workflow doc from Firestore
2. Validate authentication/authorization

Response:
{
  "workflow_id": "wf_2232bc88",
  "originalText": "customer support workflow...",
  "analysis": { /* WorkflowAnalysis JSON */ },
  "orgChart": { /* AgentOrgChart JSON or null */ },
  "approvalStatus": "PENDING|APPROVED|REJECTED",
  "approvedBy": "user_id or null",
  "approvedAt": "timestamp or null",
  "createdAt": "2025-11-18T20:10:00.000Z",
  "updatedAt": "2025-11-18T20:10:00.000Z",
  "metadata": { /* custom fields */ }
}

HTTP Status: 200 OK (if found), 404 Not Found
```

**Endpoint: `GET /workflows`**
```
Query Parameters:
- status: PENDING|APPROVED|REJECTED (optional, filter)
- limit: 10-100 (default 20)
- cursor: for pagination (optional)

Processing:
1. Query Firestore with filters and sorting
2. Order by createdAt descending

Response:
{
  "workflows": [
    {
      "workflow_id": "wf_2232bc88",
      "approvalStatus": "PENDING",
      "createdAt": "2025-11-18T20:10:00.000Z",
      "updatedAt": "2025-11-18T20:10:00.000Z"
    },
    // ... more workflows
  ],
  "cursor": "next_page_cursor_if_more_results"
}

HTTP Status: 200 OK
```

**Endpoint: `DELETE /workflows/{workflow_id}`**
```
Processing:
1. Soft or hard delete (decide based on requirements)
2. Soft delete: Set deletedAt timestamp
3. Hard delete: Remove document entirely

Response:
{
  "message": "Workflow deleted successfully",
  "workflow_id": "wf_2232bc88"
}

HTTP Status: 200 OK (success), 404 Not Found
```

#### Step 5.2 - Approval Workflow Endpoints
**New file:** `backend/api/approval.py`

**Endpoint: `POST /workflows/{workflow_id}/approve`**
```
Request:
{
  "approved_by": "generic_user",
  "notes": "Analysis looks good"
}

Processing:
1. Validate workflow exists and status is PENDING
2. Call workflow_repository.approve_workflow()
3. Org design synthesis automatically triggered inside approve_workflow()
   - Retrieves analysis
   - Runs run_org_design_for_analysis() (now that approval status == APPROVED)
   - Org chart, agentRegistry, toolRegistry auto-saved to Firestore
4. Errors during synthesis logged but don't fail the approval

Response (after approval + synthesis complete):
{
  "workflow_id": "wf_2232bc88",
  "approvalStatus": "APPROVED",
  "approvedBy": "generic_user",
  "approvedAt": "2025-11-18T20:30:00.000Z",
  "orgChart": { /* AgentOrgChart JSON */ },
  "agentRegistry": { /* Agent registry dict */ },
  "toolRegistry": { /* Tool registry dict */ },
  "updatedAt": "2025-11-18T20:31:00.000Z"
}

HTTP Status: 200 OK (success), 400 Bad Request (invalid state), 500 Server Error (synthesis failure)
```

**Note:** No separate `/synthesize-org` endpoint needed. Org design automatically triggers on approval.

#### Step 5.3 - FastAPI Application Setup
**File to modify:** `backend/__main__.py` or create `backend/api/app.py`

```python
from fastapi import FastAPI
from backend.api import workflows, approval

app = FastAPI(
    title="AgentArchitecture API",
    description="Workflow analysis and agent org design",
    version="1.0.0"
)

# Include routers
app.include_router(workflows.router)
app.include_router(approval.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Run command:** `python -m backend` or `uvicorn backend.api.app:app --reload`

---

### PHASE 6: Integration & Testing

#### Step 6.1 - End-to-End Workflow

```
1. USER SUBMITS WORKFLOW
   ↓
   POST /workflows
   ├── Generate workflow_id: "wf_a1b2c3d4"
   └── Call orchestrator.analyze_workflow(text)
       ├── 3-agent pipeline runs (~55 seconds)
       └── Creates WorkflowAnalysis

2. AUTO-SAVE (in orchestrator)
   └── workflow_repository.save_workflow_analysis()
       └── Firestore: workflows/wf_a1b2c3d4
           {approvalStatus: PENDING, analysis: {...}, orgChart: null, agentRegistry: null, toolRegistry: null}

3. RESPONSE TO USER
   └── Immediate return: workflow_id + analysis_json + status:PENDING

4. USER REVIEWS ANALYSIS (in UI)
   └── GET /workflows/wf_a1b2c3d4
       └── Firestore retrieval

5. USER APPROVES (triggers org design automatically)
   ↓
   POST /workflows/wf_a1b2c3d4/approve
   {approved_by: "generic_user"}
   └── Inside approve_workflow():
       a) Firestore: Set approvalStatus=APPROVED, approvedBy, approvedAt
       b) Retrieve analysis from Firestore
       c) Call run_org_design_for_analysis(analysis, repository)
       d) Org synthesis runs (~2-5 seconds)
       e) Firestore: Save orgChart, agentRegistry, toolRegistry
       f) Return approval response with all data

6. COMPLETE RECORD AVAILABLE
   ├── GET /workflows/wf_a1b2c3d4
   └── Full document: analysis + orgChart + registries + approval metadata
```

**Timeline for user:**
- Submit → Analysis completes (55s) → Review & approve (instant) → Org design completes (2-5s) → Full record ready
- Total: ~60 seconds from submission to complete record with org chart

#### Step 6.2 - Test Scenarios

**Test 1: Save and Retrieve Analysis**
```python
# 1. Submit workflow
analysis = orchestrator.analyze_workflow(workflow_text)
# (auto-saved in orchestrator)

# 2. Retrieve from Firestore
retrieved = repository.get_workflow_analysis(analysis.workflow_id)
assert retrieved.workflow_id == analysis.workflow_id
assert retrieved.steps == analysis.steps
```

**Test 2: Approval Flow**
```python
# 1. Save analysis (status=PENDING)
repository.save_workflow_analysis(...)

# 2. Verify status is PENDING
status = repository.get_approval_status(workflow_id)
assert status == "PENDING"

# 3. Approve
repository.approve_workflow(workflow_id, approved_by="user_123")

# 4. Verify status is APPROVED
status = repository.get_approval_status(workflow_id)
assert status == "APPROVED"
```

**Test 3: Org Design Auto-Triggers on Approval**
```python
# 1. Save analysis (status=PENDING, orgChart null)
repository.save_workflow_analysis(workflow_id, workflow_text, analysis)
assert repository.get_org_chart(workflow_id) is None

# 2. Try to synthesize org directly without approval (should fail)
with pytest.raises(ApprovalRequiredException):
    run_org_design_for_analysis(analysis, repository)

# 3. Approve (automatically triggers org design)
result = repository.approve_workflow(workflow_id, approved_by="generic_user")

# 4. Org design has completed automatically
org_chart = repository.get_org_chart(workflow_id)
assert org_chart is not None
assert org_chart.workflow_id == analysis.workflow_id

# 5. Verify registries were persisted
agent_reg = repository.get_agent_registry(workflow_id)
tool_reg = repository.get_tool_registry(workflow_id)
assert agent_reg is not None
assert tool_reg is not None
```

**Test 4: List Workflows by Status**
```python
# Save multiple workflows with different statuses
repository.save_workflow_analysis(wf_id_1, text_1, analysis_1)
repository.save_workflow_analysis(wf_id_2, text_2, analysis_2)
repository.approve_workflow(wf_id_1, "generic_user")  # Auto-triggers synthesis

# Query PENDING
pending = repository.list_workflows(approval_status="PENDING")
assert len(pending) == 1
assert pending[0]["workflow_id"] == wf_id_2

# Query APPROVED (synthesis completed)
approved = repository.list_workflows(approval_status="APPROVED")
assert len(approved) == 1
assert approved[0]["workflow_id"] == wf_id_1

# Verify org chart exists for approved
approved_doc = repository.get_workflow_full(wf_id_1)
assert approved_doc["orgChart"] is not None
assert approved_doc["agentRegistry"] is not None
assert approved_doc["toolRegistry"] is not None
```

---

## File Structure After Implementation

```
backend/
├── database/
│   ├── __init__.py
│   ├── database-plan.md                      # This file
│   ├── firebase_client.py                    # Firebase initialization
│   ├── workflow_repository.py                # WorkflowRepository class
│   ├── firestore.rules                       # NEW: Security rules
│   └── firestore.indexes.json                # NEW: Index definitions
│
├── api/
│   ├── __init__.py
│   ├── workflows.py                          # CRUD endpoints
│   └── approval.py                           # Approval workflow endpoints
│
├── agent/
│   ├── workflow_analyzer_agent/
│   │   ├── orchestrator.py                   # MODIFIED: auto-save analysis
│   │   ├── types.py                          # (no changes needed)
│   │   └── ...
│   │
│   └── org_design/
│       ├── service.py                        # MODIFIED: enforce approval, save org chart
│       └── ...
│
├── __main__.py                               # MODIFIED: start FastAPI app
├── requirements.txt                          # MODIFIED: add firebase-admin
├── .env                                      # MODIFIED: Add Firebase config vars
├── firebase-service-account.json             # NEW: Service account credentials (gitignored)
└── ...
```

---

## Advantages of Firebase Approach

| Aspect | Benefit |
|--------|---------|
| **No Infrastructure** | Serverless, auto-scaling, no servers to manage |
| **Google Integration** | Works seamlessly with google-genai, google-adk, Google Cloud |
| **Real-Time** | Built-in real-time updates for future collaborative features |
| **Security** | Firebase Rules + Authentication + Row-level security |
| **Cost** | Pay-as-you-go, free tier covers development workloads |
| **JSON Native** | Firestore is document-oriented; fits our JSON-based data perfectly |
| **Audit Trail** | Timestamps and approval metadata tracked automatically |
| **Scalability** | Handles growth from single user to enterprise workflows |
| **Compliance** | Google Cloud compliance certifications (SOC 2, ISO 27001, etc.) |

---

## Dependencies Summary

**New Python packages:**
- `firebase-admin>=6.5.0`
- `google-cloud-firestore>=2.15.0`
- `google-cloud-core>=2.4.0`
- `python-dateutil>=2.8.2`

**Existing packages leveraged:**
- `fastapi>=0.121.0` (already in requirements)
- `uvicorn>=0.38.0` (already in requirements)
- `pydantic>=2.0.0` (already in requirements)
- `google-genai` (already in requirements)

---

## Deployment Checklist

Before going to production:

- [ ] Firebase project created in Google Cloud Console
- [ ] Firestore database initialized (production mode)
- [ ] Service account created with appropriate permissions
- [ ] `firebase-service-account.json` downloaded and placed in `backend/` directory
- [ ] `backend/.env` configured with Firebase project details
- [ ] `backend/database/firestore.rules` deployed via Firebase CLI
- [ ] Firestore indexes created (via `backend/database/firestore.indexes.json`)
- [ ] All dependencies installed: `pip install -r requirements.txt`
- [ ] WorkflowRepository tests passing
- [ ] Orchestrator auto-save tested
- [ ] Approval flow tested
- [ ] Org design synthesis tested
- [ ] API endpoints tested (unit + integration)
- [ ] FastAPI app starts without errors
- [ ] Firestore security rules reviewed and locked down
- [ ] Quotas and billing alerts configured

---

## Future Enhancements

1. **Registries Persistence** (optional)
   - Currently: Derive from AgChart on read
   - Future: Cache registries in orgChart.metadata if performance becomes bottleneck

2. **Workflow Versioning**
   - Track version history of analyses
   - Allow rollback to previous analysis versions

3. **User Activity Log**
   - Separate `audit_logs` collection
   - Track who approved, when, from where

4. **Batch Operations**
   - Approve multiple workflows at once
   - Bulk org design synthesis

5. **Real-Time Collaboration**
   - Multiple users reviewing same workflow
   - Live approval notifications

6. **Export Functionality**
   - Export workflow + analysis + org chart as PDF/JSON
   - Archive completed workflows

---

## Summary

This Firebase-based architecture provides:
- **Persistent storage** for workflow artifacts (original text, analysis, org chart)
- **Approval workflow** with audit trail (approved_by, approved_at timestamps)
- **API-first design** enabling future UI, integrations, and multi-user scenarios
- **Automatic persistence** in orchestrator and org design service
- **Enforcement gates** preventing org design on unapproved workflows
- **Zero infrastructure overhead** via serverless Firebase

Implementation is broken into 6 phases, each with clear responsibilities, files to create/modify, and success criteria.
