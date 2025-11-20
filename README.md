# AgentArchitecture

A full-stack AI application that analyzes business workflows and recommends automation strategies using multi-agent analysis. It identifies which workflow steps can be automated, which require AI agents, and which need human intervention.

## Problem Statement

Businesses struggle to systematically analyze their workflows and identify automation opportunities. Key challenges include:

- **Manual Analysis**: No automated way to evaluate workflow steps for automation potential
- **Risk Blindness**: Difficulty assessing compliance, security, and operational risks
- **Agent Mapping**: Unclear which agent types (agentic RAG, tool-using, etc.) are needed
- **Human Approval**: Uncertain which steps require human-in-the-loop (HITL) intervention
- **Tool Registry**: No structured registry of available agents and tools for automation

## Solution

AgentArchitecture provides an intelligent workflow analysis platform that:

1. **Parses workflows** into discrete, analyzable steps
2. **Assesses risk** including compliance and HITL requirements
3. **Scores automation feasibility** on a 0.0-1.0 scale with determinism analysis
4. **Maps to agent types** appropriate for each step (adk_base, agentic_rag, TOOL, HUMAN)
5. **Generates org charts** and tool registries for agent deployment
6. **Surfaces insights** with actionable recommendations for optimization

## Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                       Frontend (React)                       │
│  - File upload, step analysis, dashboard, insights         │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   │ REST API
                   │
┌──────────────────▼──────────────────────────────────────────┐
│                   Backend (FastAPI)                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │    Workflow Analyzer Orchestrator                      │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │ │
│  │  │ Agent 1:     │  │ Agent 2:     │  │ Agent 3:     │ │ │
│  │  │ Parser       │  │ Risk         │  │ Automation   │ │ │
│  │  │              │  │ Assessor     │  │ Analyzer     │ │ │
│  │  │ (Sequential) │  │ (Parallel)   │  │ (Parallel)   │ │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
│                          │                                   │
│  ┌────────────────────────▼──────────────────────────────┐ │
│  │    Organization Design Module                         │ │
│  │  - AgentOrgChart  - AgentRegistry  - ToolRegistry    │ │
│  └───────────────────────────────────────────────────────┘ │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   │ Persistence
                   │
         ┌─────────▼──────────┐
         │ Firebase/Firestore │
         │   (Database)       │
         └────────────────────┘
```

### Backend Architecture

The backend uses a **distributed multi-agent system** orchestrated to analyze workflows in parallel where possible:
#### Orchestrator: WorkflowAnalyzerOrchestrator
- **Coordinates** Agent execution with dependency management
- **Merges** results from all agents into unified `WorkflowAnalysis`
- **Auto-saves** to Firestore with distributed tracing
- **Tracks** session metadata and execution metrics
- **File**: `backend/agent/workflow_analyzer_agent/orchestrator.py`

#### Agent 1: Workflow Parser (Sequential)
- **Purpose**: Extract structured workflow information
- **Inputs**: Natural language workflow description
- **Outputs**: Parsed steps with ID, description, inputs, outputs, dependencies
- **File**: `backend/agent/workflow_analyzer_agent/agents/agent1_parser.py`
- **Execution**: Sequential (required before downstream analysis)

#### Agent 2: Risk Assessor (Parallel)
- **Purpose**: Evaluate compliance, security, and operational risks
- **Inputs**: Parsed workflow steps
- **Outputs**: Risk levels (LOW/MEDIUM/HIGH/CRITICAL), compliance flags, HITL requirements
- **File**: `backend/agent/workflow_analyzer_agent/agents/agent2_risk_assessor.py`
- **Execution**: Parallel (independent of Agent 3)

#### Agent 3: Automation Analyzer (Parallel)
- **Purpose**: Determine automation feasibility and suitable agent types
- **Inputs**: Parsed workflow steps
- **Outputs**: Automation scores (0.0-1.0), determinism scores, agent type mapping, tool suggestions
- **File**: `backend/agent/workflow_analyzer_agent/agents/agent3_automation_analyzer.py`
- **Execution**: Parallel (independent of Agent 2)


#### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **LLM** | Google Gemini 2.0 Flash | Intelligent analysis and reasoning |
| **Framework** | FastAPI | High-performance async REST API |
| **SDK** | Google Agent Development Kit (ADK) | Agent implementation patterns |
| **Database** | Firebase/Firestore | Persistent workflow and analysis storage |
| **Validation** | Pydantic | Structured data models and schemas |
| **Async** | asyncio/aiohttp | Concurrent agent execution |

### Frontend Architecture

- **Framework**: React 19.2.0 (Create React App)
- **Components**: File upload, step cards, dashboard, insights
- **State**: React hooks for UI state management
- **API**: Fetch API for backend communication
- **Design**: Responsive CSS with color-coded risk visualization

### Data Flow

```
User Uploads Workflow
         │
         ▼
Frontend receives file
         │
         ▼
POST /workflows with workflow_text
         │
         ▼
WorkflowAnalyzerOrchestrator.analyze_workflow()
    │
    ├─ Run Agent 1: Parse workflow (sequential)
    │       │
    │       ▼ Parsed workflow structure
    │
    ├─ Run Agent 2 & 3 in parallel
    │  ├─ Agent 2: Assess risk
    │  └─ Agent 3: Analyze automation
    │
    └─ Merge results → WorkflowAnalysis
         │
         ▼
Auto-save to Firestore
         │
         ▼
Return analysis to frontend
         │
         ▼
Display dashboard with insights
         │
         ▼
User approves analysis
         │
         ▼
POST /workflows/{id}/approve
         │
         ▼
Generate AgentOrgChart & Registries
         │
         ▼
Save to Firestore & return
```

## Setup Instructions

### Backend Setup

#### Prerequisites
- Python 3.9+
- pip
- Google Gemini API key (free from https://aistudio.google.com/app/apikey)

#### Installation

```bash
# Navigate to project root
cd agentarchitecture

# Create and activate virtual environment
python -m venv venv

# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt
```

#### Configuration

1. **Get Gemini API Key**:
   - Visit https://aistudio.google.com/app/apikey
   - Create new API key
   - Copy the key

2. **Create `backend/.env` file**:
   ```bash
   GOOGLE_API_KEY=your-gemini-api-key-here

   # Optional Firebase configuration
   FIREBASE_PROJECT_ID=your-firebase-project-id
   FIREBASE_CREDENTIALS_PATH=./firebase-service-account.json
   FIREBASE_COLLECTION_WORKFLOWS=workflows
   ```

3. **(Optional) Setup Firebase**:
   - Create project at https://console.firebase.google.com
   - Enable Firestore Database (US region recommended)
   - Generate service account JSON from Project Settings → Service Accounts
   - Save as `backend/firebase-service-account.json`
   - Update `FIREBASE_PROJECT_ID` in `.env`

#### Running the Backend

```bash
# From backend directory
cd backend

# Option 1: Direct module execution
python -m backend

# Option 2: Uvicorn development server (recommended)
python -m uvicorn backend.api.app:app --reload --host 0.0.0.0 --port 8000

# Option 3: Python interpreter
python -c "from backend.api.app import run_server; run_server()"
```

Backend will be available at `http://localhost:8000`

Check health: `curl http://localhost:8000/health`

### Frontend Setup

#### Prerequisites
- Node.js 16+
- npm 7+

#### Installation

```bash
# Navigate to frontend directory
cd agentarchitecture/frontend

# Install dependencies
npm install
```

#### Configuration

The frontend is pre-configured to communicate with the backend at `http://localhost:8000`. If you need to change this:

Edit `frontend/src/App.js` line 22:
```javascript
const response = await fetch('http://localhost:8000/workflows', {
```

#### Running the Frontend

```bash
# From frontend directory
cd frontend

# Development server (opens browser at localhost:3000)
npm start

# Production build
npm run build

# Run tests
npm test
```

### Full Stack Startup

#### Terminal 1: Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows: or source venv/bin/activate on macOS/Linux
pip install -r requirements.txt
python -m uvicorn backend.api.app:app --reload --host 0.0.0.0 --port 8000
```

#### Terminal 2: Frontend
```bash
cd frontend
npm install
npm start
```

Then open: http://localhost:3000

## API Endpoints

### Workflow Analysis

**POST** `/workflows` - Analyze a workflow
```json
{
  "workflow_text": "Step 1: Parse customer request...",
  "workflow_name": "Customer Onboarding"
}
```

Response: `WorkflowAnalysis` object with steps, summary, insights

**GET** `/workflows` - List all workflows
- Query params: `skip=0&limit=10&status=COMPLETED`

**GET** `/workflows/{workflow_id}` - Retrieve specific workflow

**DELETE** `/workflows/{workflow_id}` - Delete a workflow

**POST** `/workflows/{workflow_id}/approve` - Approve workflow and generate org chart

**GET** `/workflows/{workflow_id}/approval-status` - Check approval status

### System Health

**GET** `/health` - Health check

**GET** `/` - API information

## Key Metrics

### Determinism Score (0.0 - 1.0)
Indicates how rule-based vs. ambiguous a workflow step is:
- **1.0**: Pure logic, API calls, deterministic rules
- **0.7-0.9**: Pattern recognition, high-confidence classification
- **0.4-0.6**: Context synthesis, generation tasks
- **0.0-0.3**: Creative work, ambiguous judgment, legal decisions

### Automation Feasibility (0.0 - 1.0)
Likelihood that a step can be successfully automated:
- **≥ 0.7**: Automatable (default threshold)
- **0.4-0.7**: Possible with mitigation
- **< 0.4**: Manual or HITL required

### Risk Levels
- **LOW**: Minimal risk, clear automation path
- **MEDIUM**: Some ambiguity, manageable risk
- **HIGH**: Significant risk, requires careful planning
- **CRITICAL**: Compliance/legal risk, requires HITL

## Key Components

### Backend Schemas
- **WorkflowStep**: Individual step with risk, automation, and agent data
- **WorkflowAnalysis**: Complete analysis with summary and insights
- **AgentOrgChart**: Hierarchical structure of agents
- **AgentRegistry**: Catalog of available agents and capabilities
- **ToolRegistry**: Available tools and APIs for automation

### Frontend Components
- **FileUpload**: Drag-and-drop workflow file upload
- **StepsList**: Grid displaying all analyzed workflow steps
- **StepCard**: Individual step with risk badge, automation score, agent type
- **SummaryContainer**: Dashboard metrics and statistics
- **KeyInsights**: Actionable insights with priority levels

## Project Structure

```
agentarchitecture/
├── backend/
│   ├── agent/
│   │   ├── workflow_analyzer_agent/
│   │   │   ├── agents/
│   │   │   │   ├── agent1_parser.py          # Workflow parsing
│   │   │   │   ├── agent2_risk_assessor.py   # Risk assessment
│   │   │   │   └── agent3_automation_analyzer.py  # Automation analysis
│   │   │   ├── orchestrator.py               # Agent orchestration
│   │   │   ├── config.py                     # Configuration
│   │   │   └── prompts.py                    # LLM prompts
│   │   └── org_design/
│   │       └── org_design_generator.py       # Org chart generation
│   ├── api/
│   │   ├── app.py                            # FastAPI application
│   │   ├── routes.py                         # API endpoints
│   │   └── models.py                         # Pydantic schemas
│   ├── database/
│   │   └── firebase_service.py               # Firestore integration
│   ├── schemas/
│   │   └── workflow_schemas.py               # Data models
│   └── requirements.txt                      # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── FileUpload.js
│   │   │   ├── StepsList.js
│   │   │   ├── StepCard.js
│   │   │   └── ...
│   │   ├── utils/
│   │   └── App.js
│   ├── public/
│   └── package.json
└── README.md                                 # This file
```

## Decision Rationale: Backend Architecture

### Multi-Agent Distributed System
**Why**: Workflow analysis has distinct phases (parsing, risk assessment, automation analysis) that can be parallelized after parsing.

**Benefit**: Agent 2 and 3 run simultaneously after Agent 1 completes, reducing total analysis time while maintaining dependency integrity.

### Google Gemini 2.0 Flash
**Why**: Latest frontier model optimized for speed and reasoning.

**Benefit**: Fast response times for interactive web application; excellent reasoning for complex workflow analysis.

### FastAPI
**Why**: Modern async Python framework with automatic OpenAPI documentation.

**Benefit**: Native async/await support for concurrent agent execution; clean, intuitive API design.

### Firebase/Firestore
**Why**: Serverless NoSQL database with real-time capabilities and built-in security.

**Benefit**: No database server setup; automatic scaling; real-time updates potential; JSON-native storage for workflow data.

### Pydantic Models
**Why**: Strong data validation at API boundaries and agent outputs.

**Benefit**: Type safety; automatic validation; clear schema documentation; prevents invalid data propagation.

## Example Workflow Analysis

**Input**:
```
"Customer request comes in, we parse it, check inventory with our database API,
if inventory is available we create an order, if not we notify customer with email"
```

**Output Summary**:
- **Total Steps**: 4 (parse, check inventory, create order, notify)
- **Automatable**: 3 of 4 (75%)
- **Agent Types**: 1 adk_base, 2 agentic_rag, 1 HUMAN
- **Risks**: 1 HIGH (inventory API dependency), 1 MEDIUM (customer notification)
- **Automation Potential**: 0.82

**Agent Assignments**:
- **Parse request**: agentic_rag (NLP required) - 0.9 automation
- **Check inventory**: adk_base (API call) - 1.0 automation
- **Create order**: adk_base (deterministic) - 0.95 automation
- **Notify customer**: HUMAN (requires judgment on tone) - 0.4 automation

## Troubleshooting

### Backend Issues

**Port already in use**:
```bash
# Change port
python -m uvicorn backend.api.app:app --reload --port 8001
```

**Google API key invalid**:
- Verify key in `.env` file
- Check API is enabled in Google AI Studio
- Ensure no extra whitespace in key

**Firestore connection errors**:
- Verify credentials file path
- Check Firebase project ID
- Ensure Firestore database is created

### Frontend Issues

**Cannot connect to backend**:
- Verify backend is running on port 8000
- Check URL in `frontend/src/App.js`
- Browser console for CORS errors

**npm install fails**:
```bash
npm cache clean --force
rm package-lock.json
npm install
```

## Development

### Running Tests

```bash
# Backend unit tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Building for Production

```bash
# Frontend
cd frontend
npm run build

# Backend can be deployed as-is with ASGI server:
# Use gunicorn, Uvicorn, or cloud platform (Cloud Run, App Engine, etc.)
```

## License

[Add your license here]

## Contributors

[Add contributors here]

## Resources

- [Google Gemini API Docs](https://ai.google.dev/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Firebase Documentation](https://firebase.google.com/docs)
- [React Documentation](https://react.dev/)
- [Google Agent Development Kit](https://cloud.google.com/docs/agent-development-kit)
