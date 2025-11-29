# Calibrate

## Core Concept and Value

Calibrate is a full-stack AI assistant that inspects business workflows, flags which steps can be automated, shows where AI fits, and calls out when humans must remain in the loop, giving teams an honest read on AI limits. The Google Agent Development Kit (ADK) powers this multi-agent system, which combines agent evaluation of stored workflow analyses with a production-ready FastAPI deployment backed by Firestore.

### Problem Statement

Teams don’t know which tasks AI can handle and overdo the hand-off, leading to:
- **Blind spots** around automation feasibility, compliance, and HITL risk
- **Unclear mapping** of step-level needs to agent types vs. humans
- **No shared registry** of org-approved tools, agents, and integrations
- **Failed automation rollouts** waste resources on steps AI can’t own end-to-end

### Solution

Calibrate helps teams confidently automate by:
1. Parsing free-form workflows into structured steps
2. Scoring automation feasibility and determinism per step
3. Highlighting compliance/HITL risks with mitigation notes
4. Reviewing automation potential, risks, and per-step opportunities
5. Recommending agent types, tools, and registries for deployment

## Course Concepts Demonstrated

**Multi-agent system** – WorkflowAnalyzerOrchestrator chains sequential (Parser → Summarizer) and parallel (Risk + Automation) agents powered by Gemini and ADK, with an additional deterministic org-design module triggered post-approval.

**Agent evaluation** – Each run saves a complete `WorkflowAnalysis` (steps, scores, recommendations) that we replay against golden workflows to compare automation/risk deltas and catch regressions before approving org designs.

**Agent deployment** – FastAPI exposes `/workflows` and `/workflows/{id}/approve`, letting the multi-agent workflow run end-to-end in a production-style REST service backed by Firestore.

Also uses shared session state, ADK tool hooks, and orchestrator tracing/metrics with retries.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                       Frontend (React)                      │
│  - File upload, dashboards, insights, approvals             │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   │ REST API
                   │
┌──────────────────▼──────────────────────────────────────────┐
│                   Backend (FastAPI)                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         Workflow Analyzer Orchestrator                 │ │
│  │        ┌──────────────┐                                │ │
│  │        │ Agent 1:     │                                │ │
│  │        │ Parser       │                                │ │
│  │        │ (Sequential) │                                │ │
│  │        └────┬────┬────┘                                │ │
│  │             │    │                                     │ │
│  │  ┌──────────▼┐   ┌▼──────────────┐                     │ │
│  │  │ Agent 2:  │   │ Agent 3:      │                     │ │
│  │  │ Risk      │   │ Automation    │                     │ │
│  │  │ Assessor  │   │ Analyzer      │                     │ │
│  │  │ (Parallel)│   │ (Parallel)    │                     │ │
│  │  └───────────┘   └──────────────┘                     │ │
│  │         │  (risks → session)   │ (automation → session)│ │
│  │         └────────┬─────────────┘                       │ │
│  │                  ▼                                     │ │
│  │          ┌──────────────────────┐                      │ │
│  │          │ Agent 4: Summarizer  │                      │ │
│  │          │ (reads session data) │                      │ │
│  │          │ Quick wins & roadmap │                      │ │
│  │          └──────────────────────┘                      │ │
│  │                   │                                    │ │
│  │                   ▼                                    │ │
│  │        Human-in-the-loop Approval                      │ │
│  │      (POST /workflows/{id}/approve)                    │ │
│  │                   │                                    │ │
│  └───────────────────▼────────────────────────────────────┘ │
│                           │                                 │
│  ┌────────────────────────▼──────────────────────────────┐  │
│  │    Organization Design Module                         │  │
│  │  - AgentOrgChart  - AgentRegistry  - ToolRegistry     │  │
│  └───────────────────────────────────────────────────────┘  │
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

A distributed multi-agent pipeline shares a `SessionState` so each stage can reuse prior outputs. The `WorkflowAnalyzerOrchestrator` (`backend/agent/workflow_analyzer_agent/orchestrator.py`) coordinates sequential and parallel tasks, retries transient failures, and persists the final `WorkflowAnalysis`.

Agent 1: Parser (`agent1_parser.py`)
Turns natural-language workflows into structured steps with IDs, dependencies, and IO so downstream agents know what to analyze. 

Agent 2: Risk Assessor (`agent2_risk_assessor.py`)
Reads those steps and writes compliance/security/HITL scores plus mitigation notes to `session.risks`. 

Agent 3: Automation Analyzer (`agent3_automation_analyzer.py`)
Evaluates determinism and automation feasibility per step, recommending agent types and tool hooks in `session.automation`.

Agent 4: Summarizer (`agent4_automation_summarizer.py`)
Ingests the whole session to draft quick wins and phased roadmaps.

Human triggers approval `POST /workflows/{id}/approve` and the non-agentic org design module (`agent/org_design/service.py`) deterministically produces the `AgentOrgChart`, `AgentRegistry`, and `ToolRegistry`.

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

React 19.2 (CRA) powers the UI, which uses hooks for state, Fetch for API calls, and responsive CSS to highlight risk/automation insights across FileUpload, StepsList/StepCard, Summary, and KeyInsights components.

## Scoring System

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

## Setup Instructions

### Backend (run first)

**Prerequisites**: Python 3.9+, pip, and a Google Gemini API key from https://aistudio.google.com/app/apikey.

```bash
cd agentarchitecture/backend
python -m venv venv
source venv/bin/activate       # macOS/Linux
venv\Scripts\activate          # Windows PowerShell/CMD
pip install -r requirements.txt
```

Create `backend/.env` with your Gemini key and optional Firebase settings:

```
GOOGLE_API_KEY=your-gemini-api-key-here
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_CREDENTIALS_PATH=./firebase-service-account.json
FIREBASE_COLLECTION_WORKFLOWS=workflows
```

Provision Firebase only if you need persistence: create a project, enable Firestore, download a service account JSON, and update the env values accordingly.

Start the API:
```bash
python -m uvicorn backend.api.app:app --reload --host 0.0.0.0 --port 8000
```
Health check: `curl http://localhost:8000/health`

### Frontend

**Prerequisites**: Node.js 16+ and npm 7+. The default API base is `http://localhost:8000`; update `frontend/src/App.js` if you change it.

```bash
cd agentarchitecture/frontend
npm install
npm start   # opens http://localhost:3000
```

### Verify

With the backend running in one terminal and the frontend in another, visit `http://localhost:3000`. Upload a workflow and confirm the app displays analysis returned from `http://localhost:8000`.

## API Endpoints

Primary workflow call:
```http
POST /workflows
{
  "workflow_text": "Step 1: Parse customer request...",
  "workflow_name": "Customer Onboarding"
}
```
Returns a `WorkflowAnalysis` containing parsed steps, risk notes, automation scores, and a summary.

Other endpoints:
- `GET /workflows` – List workflows (`skip`, `limit`, `status` filters)
- `GET /workflows/{workflow_id}` – Fetch a single workflow
- `DELETE /workflows/{workflow_id}` – Remove a workflow
- `POST /workflows/{workflow_id}/approve` – Trigger org-chart generation
- `GET /workflows/{workflow_id}/approval-status` – Check HITL approval state
- `GET /health` – Service health probe
- `GET /` – API metadata

## Key Components

Backend schemas cover `WorkflowStep`, `WorkflowAnalysis`, and the org-design artifacts (`AgentOrgChart`, `AgentRegistry`, `ToolRegistry`). On the frontend, the primary components are FileUpload, StepsList/StepCard, SummaryContainer, and KeyInsights for surfacing insights.

## Project Structure

```
agentarchitecture/
├── backend/
│   ├── agent/
│   │   ├── workflow_analyzer_agent/
│   │   │   ├── agents/
│   │   │   │   ├── agent1_parser.py          # Workflow parsing
│   │   │   │   ├── agent2_risk_assessor.py   # Risk assessment
│   │   │   │   ├── agent3_automation_analyzer.py  # Automation analysis
│   │   │   │   └── agent4_automation_summarizer.py # Automation summary & roadmap
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

## Technical Choices

We opted for a multi-agent design so parsing happens once and risk/automation analysis run in parallel, all coordinated through FastAPI’s async stack. Google Gemini 2.0 Flash provides fast reasoning for each agent, while Pydantic schemas enforce clean inputs/outputs before data is saved. Firestore supplies serverless persistence that mirrors the JSON objects our agents produce, keeping deployment lightweight.

## Troubleshooting

- **Backend**: If port 8000 is busy, rerun Uvicorn with `--port 8001`. Invalid Gemini keys usually stem from typos in `backend/.env` or the API not being enabled in Google AI Studio. Firestore errors typically mean the service-account path or project ID doesn’t match your Firebase project, or Firestore hasn’t been initialized.
- **Frontend**: Connection issues are almost always a backend that isn’t running on `http://localhost:8000` or a stale URL in `frontend/src/App.js`. When `npm install` fails, clear the cache (`npm cache clean --force`), delete `package-lock.json`, and reinstall.

## License

Licensed under CC BY 4.0.

## Contributors

Calvin Cheng
Lisa Gu
