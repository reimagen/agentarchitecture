# Step 1: Core Infrastructure Setup

**Estimated Time:** 1 hour
**Status:** Not Started
**Goal:** Create the foundational components for session management and observability

## Tasks

### 1.1 Create Session Management
**File:** `session/session_state.py`

Create the `SessionState` dataclass with fields:
- `session_id`: Unique identifier for this analysis session
- `trace_id`: For distributed tracing across all agents
- `created_at`: Timestamp when session was created
- `parsed_steps`: Store Agent 1 output
- `risks`: Store Agent 2 output (Risk Assessment)
- `automation`: Store Agent 3 output (Automation Analysis)
- `final_analysis`: Merged final result
- `agent1_latency`, `agent2_latency`, `agent3_latency`: Timing metrics
- `parallel_start_time`, `parallel_end_time`: Track parallel execution window
- `tool_calls`: List of tool calls made (for metrics)
- `errors`: List of errors encountered (for metrics)

**File:** `session/session_manager.py`

Create the `SessionManager` class with:
- `create_session()` → returns new `SessionState` with generated UUIDs
- `get_session(session_id: str)` → retrieves session (for now, in-memory storage)

### 1.2 Create Structured Logging
**File:** `observability/logger.py`

Create the `StructuredLogger` class with methods:
- `info(msg: str, **kwargs)` → JSON-formatted INFO logs with timestamp
- `debug(msg: str, **kwargs)` → JSON-formatted DEBUG logs
- `warning(msg: str, **kwargs)` → JSON-formatted WARNING logs
- `error(msg: str, **kwargs)` → JSON-formatted ERROR logs

Each log entry should include:
- `timestamp`: ISO format
- `level`: INFO, DEBUG, WARNING, ERROR
- `message`: The log message
- Additional context passed via `**kwargs`

### 1.3 Create Distributed Tracing
**File:** `observability/tracer.py`

Create the `DistributedTracer` class with:
- `span(trace_id: str, span_id: str, operation: str)` → context manager
- Tracks duration of operations
- Stores spans with structure: `{span_id, operation, duration_ms, status}`
- Spans grouped by `trace_id`

### 1.4 Create Metrics Collection
**File:** `observability/metrics.py`

Create the `MetricsCollector` class with:
- `record_latency(agent: str, latency_ms: float)` → stores latency values
- `record_tool_call(tool_name: str, duration_ms: float)` → increments tool call counter
- `record_analysis(session: SessionState)` → records overall analysis metrics
- `get_summary()` → returns dict of all collected metrics

Metrics to track:
- `analyses_total`: Number of analyses run
- `agent_1_parser_latency`: Agent 1 latency histogram
- `agent_2_risk_latency`: Agent 2 latency histogram
- `agent_3_automation_latency`: Agent 3 latency histogram
- `tool_api_lookup_calls`: Counter for api_lookup tool calls
- `tool_compliance_calls`: Counter for compliance_checker tool calls

### 1.5 Create Configuration File
**File:** `config.py`

Define constants:
```python
MODEL = "gemini-2.0-flash-exp"
TEMPERATURE = 0.1  # Low for consistency
TIMEOUT = 30  # seconds
MAX_WORKFLOW_LENGTH = 10000  # characters
MIN_WORKFLOW_LENGTH = 10

AGENT_TYPES = ["adk_base", "agentic_rag", "TOOL", "HUMAN"]
RISK_LEVELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
AUTOMATION_FEASIBLE_THRESHOLD = 0.6
```

### 1.6 Create Type Definitions
**File:** `types.py`

Define Pydantic models (using `from pydantic import BaseModel`):
- `ParsedWorkflow`: List of parsed steps from Agent 1
- `WorkflowStep`: Individual step with all fields (id, description, inputs, outputs, dependencies, agent_type, scores, risk, etc.)
- `RiskAssessment`: Risk data for a step (step_id, risk_level, requires_hitl, notes)
- `AutomationData`: Automation analysis for a step (step_id, agent_type, determinism_score, automation_feasibility, notes)
- `AutomationSummary`: Summary stats (total_steps, automatable_count, agent_required_count, human_required_count, automation_potential)
- `WorkflowAnalysis`: Final output with all steps, summary, key_insights, risks_and_compliance
- `AnalysisMetrics`: Metrics for a completed analysis

## Acceptance Criteria

- [ ] All 6 files created with correct structure
- [ ] SessionState is a proper dataclass with all fields
- [ ] SessionManager can create sessions with unique IDs
- [ ] StructuredLogger produces JSON-formatted logs
- [ ] DistributedTracer tracks spans with timing
- [ ] MetricsCollector stores and retrieves metrics
- [ ] Config.py has all constants defined
- [ ] Types.py has all Pydantic models defined
- [ ] No import errors when importing each module
- [ ] All classes can be instantiated without errors

## Notes

- Keep each module focused on a single responsibility
- Use `import uuid` for generating unique IDs
- Use `from datetime import datetime` for timestamps
- Use Python's `logging` module for the StructuredLogger
- Use `@dataclass` for SessionState (from `dataclasses`)
- Use `BaseModel` from Pydantic for type definitions

## Next Step

→ Once complete, move to **Step 2: Custom Tools Implementation**
