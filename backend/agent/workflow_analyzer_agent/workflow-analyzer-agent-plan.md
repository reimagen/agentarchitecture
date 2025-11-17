# Phase 1.3: Build the ADK Workflow Analyzer Agent - Detailed Plan

## Overview
Create a **multi-agent system** using `gemini-2.0-flash-exp` that analyzes workflow text and outputs valid JSON recommendations for automation using Google ADK agent types.

**Architecture:** 3 sequential agents + custom tools + session state management + full observability (logging, tracing, metrics)

**Estimated Time:** 2-3 hours
**Key Constraint:** Agent must reliably output valid JSON, no fallback text generation

**Course Requirements Met:**
- ✅ Multi-agent system (3 sequential agents)
- ✅ LLM-powered agents
- ✅ Sequential agents with state passing
- ✅ Custom tools (API lookup, compliance checker)
- ✅ Sessions & state management
- ✅ Context engineering (detailed prompts)
- ✅ Observability (logging, tracing, metrics)

---

## 1. Architecture & Design

### 1.1 Agent Purpose
- **Input:** Plain text workflow description (steps, dependencies, actors)
- **Process:** 3 sequential agents analyze workflow in stages
- **Output:** Structured JSON matching the Pydantic schema
- **Success Metric:** 100% valid JSON output, 80%+ sensible recommendations
- **Observability:** Full tracing, logging, and metrics across all agents

### 1.2 Sequential + Parallel Agent System Architecture

```
Input Workflow Text
        ↓
    [Session Created] ← (Session State Manager)
        ↓
┌─────────────────────────────────────┐
│ AGENT 1: Workflow Parser            │ (SEQUENTIAL - must run first)
├─────────────────────────────────────┤
│ • Parse workflow text               │
│ • Extract steps, dependencies       │
│ • Identify inputs/outputs           │
│ • Store in session.parsed_steps     │
│ • Log: step count, parsing time     │
└─────────────────────────────────────┘
        ↓ (context passed via session)
    ┌───┴────────────────────────────────┐
    ↓                                     ↓
┌──────────────────────┐      ┌──────────────────────────┐
│ AGENT 2:             │      │ AGENT 3:                 │
│ Risk & Compliance    │      │ Automation Analyzer      │
│ Assessor             │      │                          │
├──────────────────────┤      ├──────────────────────────┤
│ • Evaluate risk      │      │ • Determine agent types  │
│ • Call custom tool:  │      │ • Score determinism &    │
│   get_compliance_    │      │   feasibility            │
│   rules()            │      │ • Call custom tool:      │
│ • Store in          │      │   lookup_api_docs()      │
│   session.risks      │      │ • Store in              │
│ • Log: risk levels,  │      │   session.automation     │
│   tool calls         │      │ • Log: agent types,      │
│ (PARALLEL)           │      │   scores (PARALLEL)      │
└──────────────────────┘      └──────────────────────────┘
    ↓                                     ↓
    └───┬────────────────────────────────┘
        ↓ (both outputs merged via session)
┌─────────────────────────────────────┐
│ ORCHESTRATOR: Merge Results         │
├─────────────────────────────────────┤
│ • Wait for Agent 2 & 3 to complete  │
│ • Merge risks + automation analysis │
│ • Compile final WorkflowAnalysis    │
│ • Store in session.final_analysis   │
└─────────────────────────────────────┘
        ↓
    [Metrics Collected]
        ↓
    Output: Complete WorkflowAnalysis JSON
```

**Flow Summary:**
- **Agent 1 (Sequential):** Parses workflow, outputs structured steps
- **Agent 2 & 3 (Parallel):** Both run simultaneously after Agent 1 finishes
  - Agent 2: Assesses risk for each step (no dependency on Agent 3)
  - Agent 3: Analyzes automation potential (no dependency on Agent 2)
- **Orchestrator:** Waits for both agents, merges results, produces final JSON

**Course Requirements Met:**
- ✅ Sequential agents (Agent 1 before Agent 2/3)
- ✅ Parallel agents (Agent 2 & 3 run concurrently)

### 1.3 Core Components

#### Component 1: Orchestrator (Sequential + Parallel)
```
WorkflowAnalyzerOrchestrator
├── __init__()
│   ├── Initialize session manager
│   ├── Initialize 3 agents
│   ├── Initialize custom tools
│   └── Initialize observability (logger, tracer, metrics)
├── analyze_workflow(workflow_text: str) → WorkflowAnalysis
│   ├── Create session (session_id, trace_id)
│   ├── [SEQUENTIAL] Run Agent1.parse() → update session.parsed_steps
│   ├── [PARALLEL] Launch both:
│   │   ├── Agent2.assess_risk() → update session.risks (async)
│   │   └── Agent3.analyze_automation() → update session.automation (async)
│   ├── Wait for both Agent 2 & 3 to complete (asyncio.gather)
│   ├── Merge results: combine risks + automation into final analysis
│   ├── Collect metrics from all agents
│   └── Return WorkflowAnalysis
└── get_analysis_metrics() → AnalysisMetrics
    └── Return timing, tokens, errors, tool calls, parallel execution time
```

#### Component 2: Individual Agents

**Agent 1: Workflow Parser**
- Input: workflow_text
- Output: ParsedWorkflow (steps, dependencies)
- Prompt: "Parse this workflow into structured steps"
- Logging: Step count, parsing latency, validation errors

**Agent 2: Risk & Compliance Assessor**
- Input: ParsedWorkflow (from session)
- Custom Tool: `get_compliance_rules(risk_level, domain)`
- Output: RiskAssessment (per-step risks)
- Logging: Tool calls, risk classifications, latency
- Tracing: Show which steps were high-risk

**Agent 3: Automation Analyzer**
- Input: ParsedWorkflow + RiskAssessment (from session)
- Custom Tool: `lookup_api_docs(step_description)`
- Output: FinalAnalysis (agent types, scores)
- Logging: Agent type assignments, feasibility scores
- Tracing: Show reasoning for high-touch steps

#### Component 3: Custom Tools

**Tool 1: `lookup_api_docs(step_description: str) → dict`**
```python
# Returns: {"api_exists": bool, "api_name": str, "determinism": float, "notes": str}
# Example: "Send email" → {"api_exists": True, "api_name": "Gmail API",
#                           "determinism": 1.0, "notes": "Fully deterministic"}
# Used by: Agent 3 to determine if a step is automatable
```

**Tool 2: `get_compliance_rules(risk_level: str, domain: str) → dict`**
```python
# Returns: {"applicable_rules": [str], "requires_audit": bool, "hitl_required": bool}
# Example: risk_level="CRITICAL", domain="financial" →
#          {"applicable_rules": ["SOX", "PCI-DSS"], "requires_audit": True, "hitl_required": True}
# Used by: Agent 2 to determine compliance requirements
```

#### Component 4: Session State Manager
- Maintains state across sequential agents
- Stores: parsed_steps, risk_assessments, final_analysis
- Tracks: session_id, trace_id, creation_time
- Enables: context passing between agents

#### Component 5: Observability Stack

**Logging:**
```python
# Each agent logs at multiple levels
logger.info(f"[{session_id}] Agent 1 started parsing workflow")
logger.debug(f"[{session_id}] Found {step_count} steps with {dependency_count} dependencies")
logger.warning(f"[{session_id}] Step 5 has circular dependency")
logger.error(f"[{session_id}] JSON parse failed, retrying...")
```

**Tracing:**
```python
# Distributed tracing across all agents
trace_id = generate_uuid()
agent1_span = tracer.span(f"{trace_id}_agent1", "workflow_parser")
agent2_span = tracer.span(f"{trace_id}_agent2", "risk_assessor")
agent3_span = tracer.span(f"{trace_id}_agent3", "automation_analyzer")
# Shows: Agent 1 → 200ms, Agent 2 → 1500ms (includes 2 tool calls), Agent 3 → 800ms
```

**Metrics:**
```python
metrics.counter("workflow_analyses_total", tags={"status": "success"})
metrics.histogram("agent_latency_ms", agent1_latency, tags={"agent": "parser"})
metrics.histogram("tool_calls", 2, tags={"tool": "api_lookup"})
metrics.gauge("tokens_used", 3500, tags={"agent": "risk_assessor"})
metrics.gauge("automation_potential", 0.65, tags={"workflow": "customer_support"})
```

---

## 2. System Prompt Deep Dive

### 2.1 Prompt Goals
1. **Clarity:** Agent understands exactly what to analyze
2. **Consistency:** Same workflow → consistent recommendations
3. **JSON Compliance:** Output MUST be valid JSON (no markdown, no extra text)
4. **Scoring Logic:** Clear rules for determinism, feasibility, risk

### 2.2 System Prompt Structure

**Section A: Role & Context**
- You are a workflow automation analyst
- You understand Google ADK agent capabilities
- You evaluate workflows for automation potential

**Section B: ADK Agent Types (Definitions)**
```
- adk_base: Simple deterministic tasks (data processing, API calls, structured workflows)
- agentic_rag: Retrieval-Augmented Generation (Q&A, knowledge lookup, document analysis)
- TOOL: Single function/tool execution (one-off actions, external integrations)
- HUMAN: Requires human judgment, creativity, complex decisions, exception handling
```

**Section C: Scoring Guidelines**

**Determinism Score (0.0 - 1.0):**
```
1.0   → API call, database query, deterministic rule-based logic
0.8   → Structured workflow with minor variability
0.5   → Some judgment required, but guidelines exist
0.3   → Significant judgment, multiple valid approaches
0.0   → Highly creative, subjective, unpredictable outcomes
```

**Automation Feasibility Score (0.0 - 1.0):**
```
1.0   → Fully automatable, clear inputs/outputs, no blockers
0.8   → Mostly automatable, minor human input needed for validation
0.6   → Automatable with conditions or fallback to HUMAN agent
0.4   → Possible to automate but high risk or cost
0.0   → Cannot be automated with current tools, requires human judgment
```

**Risk Level:**
```
LOW       → Standard operations, well-tested patterns
MEDIUM    → Some complexity, moderate impact if wrong
HIGH      → Financial, legal, or customer-impacting consequences
CRITICAL  → Regulatory, security, safety implications
```

**Section D: Output Format (JSON Schema)**
Include example JSON output showing:
- Proper structure for WorkflowStep
- Proper structure for AutomationSummary
- All required fields populated

**Section E: Instructions for JSON Output**
- "You MUST respond with ONLY valid JSON, no other text"
- "Do not include markdown code fences"
- "Do not include explanatory text before or after JSON"
- "Ensure all fields match the schema exactly"

---

## 3. User Prompt Template

### 3.1 Structure
```
WORKFLOW_NAME: [extracted or provided]
WORKFLOW_TEXT:
[user's workflow description]

ANALYSIS_TASK:
1. Analyze each step in the workflow
2. For each step, determine:
   - ID (step_N)
   - Description (from workflow text)
   - Inputs (what's needed to start)
   - Outputs (what it produces)
   - Dependencies (which steps must finish first)
   - Best agent type (adk_base, agentic_rag, TOOL, HUMAN)
   - Determinism score (0.0-1.0)
   - Automation feasibility (0.0-1.0)
   - Risk level (LOW, MEDIUM, HIGH, CRITICAL)
   - Requires HITL (true/false)
   - Notes (recommendations, blockers, improvements)

3. Calculate summary statistics:
   - Total steps
   - Automatable count (score >= 0.6)
   - Agent required count (not HUMAN)
   - Human required count (HUMAN agent)
   - Automation potential (automatable / total)

4. Identify key insights (2-5 findings)

5. Identify risks and compliance considerations

OUTPUT: Return ONLY valid JSON matching the schema
```

---

## 4. Implementation Details

### 4.1 File Structure
```
backend/agent/workflow-analyzer-agent/
├── workflow-analyzer-agent-plan.md      (this file)
├── orchestrator.py                      (WorkflowAnalyzerOrchestrator - main entry)
├── agents/
│   ├── __init__.py
│   ├── agent1_parser.py                 (Workflow Parser Agent)
│   ├── agent2_risk_assessor.py          (Risk & Compliance Assessor Agent)
│   └── agent3_automation_analyzer.py    (Automation Analyzer Agent)
├── tools/
│   ├── __init__.py
│   ├── api_lookup.py                    (Custom tool: lookup_api_docs)
│   └── compliance_checker.py            (Custom tool: get_compliance_rules)
├── session/
│   ├── __init__.py
│   ├── session_manager.py               (Session State Management)
│   └── session_state.py                 (SessionState data class)
├── observability/
│   ├── __init__.py
│   ├── logger.py                        (Structured logging)
│   ├── tracer.py                        (Distributed tracing)
│   └── metrics.py                       (Metrics collection)
├── prompts.py                           (System prompts for each agent)
├── config.py                            (Constants, configuration)
└── types.py                             (Pydantic models, type definitions)
```

### 4.2 Main Orchestrator Class

**WorkflowAnalyzerOrchestrator:**

```python
class WorkflowAnalyzerOrchestrator:
    def __init__(self, model: str = "gemini-2.0-flash-exp"):
        self.model = model
        self.client = genai.Client()

        # Initialize components
        self.session_manager = SessionManager()
        self.logger = StructuredLogger(__name__)
        self.tracer = DistributedTracer()
        self.metrics = MetricsCollector()

        # Initialize agents
        self.agent1_parser = WorkflowParserAgent(
            client=self.client,
            logger=self.logger,
            tracer=self.tracer
        )
        self.agent2_risk_assessor = RiskAssessorAgent(
            client=self.client,
            logger=self.logger,
            tracer=self.tracer,
            tools={"get_compliance_rules": get_compliance_rules}
        )
        self.agent3_automation_analyzer = AutomationAnalyzerAgent(
            client=self.client,
            logger=self.logger,
            tracer=self.tracer,
            tools={"lookup_api_docs": lookup_api_docs}
        )

    async def analyze_workflow(self, workflow_text: str) -> WorkflowAnalysis:
        """
        Orchestrate sequential + parallel agents to analyze workflow.

        Session flow:
        1. Create session with trace_id
        2. [SEQUENTIAL] Agent 1: Parse workflow → session.parsed_steps
        3. [PARALLEL] Agent 2 & 3 run simultaneously:
           - Agent 2: Assess risk → session.risks
           - Agent 3: Analyze automation → session.automation
        4. Merge results from Agent 2 & 3
        5. Collect metrics and return final WorkflowAnalysis
        """
        # Create session
        session = self.session_manager.create_session()
        trace_id = session.trace_id

        self.logger.info(f"[{trace_id}] Starting workflow analysis")

        try:
            # [SEQUENTIAL] AGENT 1: Parse workflow
            with self.tracer.span(trace_id, "agent1_parse", "workflow_parser"):
                self.logger.info(f"[{trace_id}] Running Agent 1: Workflow Parser (SEQUENTIAL)")
                parsed = self.agent1_parser.parse(workflow_text, session)
                session.parsed_steps = parsed
                self.logger.debug(f"[{trace_id}] Agent 1 found {len(parsed)} steps")

            # [PARALLEL] AGENT 2 & 3: Run simultaneously
            self.logger.info(f"[{trace_id}] Launching Agent 2 & 3 (PARALLEL)")
            agent2_task = asyncio.create_task(
                self._run_agent2(session, workflow_text, trace_id)
            )
            agent3_task = asyncio.create_task(
                self._run_agent3(session, workflow_text, trace_id)
            )

            # Wait for both agents to complete
            risks, automation = await asyncio.gather(agent2_task, agent3_task)
            session.risks = risks
            session.automation = automation
            self.logger.info(f"[{trace_id}] Both Agent 2 & 3 completed (PARALLEL)")

            # Merge results and create final analysis
            with self.tracer.span(trace_id, "merge_results", "result_merger"):
                self.logger.info(f"[{trace_id}] Merging results from Agent 2 & 3")
                final_analysis = self._merge_results(session)
                session.final_analysis = final_analysis
                self.logger.info(f"[{trace_id}] Analysis complete. Automation potential: {final_analysis.summary.automation_potential}")

            # Collect metrics
            self.metrics.record_analysis(session)
            self.logger.info(f"[{trace_id}] Workflow analysis succeeded")

            return final_analysis

        except Exception as e:
            self.logger.error(f"[{trace_id}] Workflow analysis failed: {str(e)}")
            self.metrics.record_error(trace_id, str(e))
            raise

    async def _run_agent2(self, session: Session, workflow_text: str, trace_id: str):
        """Run Agent 2 (Risk Assessor) with tracing"""
        with self.tracer.span(trace_id, "agent2_risk", "risk_assessor"):
            self.logger.info(f"[{trace_id}] Running Agent 2: Risk Assessor (PARALLEL)")
            risks = self.agent2_risk_assessor.assess_risk(session, workflow_text)
            self.logger.debug(f"[{trace_id}] Agent 2 identified {len(risks)} risk items")
            return risks

    async def _run_agent3(self, session: Session, workflow_text: str, trace_id: str):
        """Run Agent 3 (Automation Analyzer) with tracing"""
        with self.tracer.span(trace_id, "agent3_automation", "automation_analyzer"):
            self.logger.info(f"[{trace_id}] Running Agent 3: Automation Analyzer (PARALLEL)")
            automation = self.agent3_automation_analyzer.analyze(session, workflow_text)
            self.logger.debug(f"[{trace_id}] Agent 3 determined agent types and scores")
            return automation

    def _merge_results(self, session: Session) -> WorkflowAnalysis:
        """Merge results from Agent 2 (risks) and Agent 3 (automation) into final analysis"""
        # Combine parsed_steps with risks + automation data
        merged_steps = []
        for step in session.parsed_steps:
            # Find matching risk assessment and automation analysis
            risk_data = next((r for r in session.risks if r.step_id == step.step_id), None)
            auto_data = next((a for a in session.automation if a.step_id == step.step_id), None)

            # Merge all information into single WorkflowStep
            merged_step = WorkflowStep(
                step_id=step.step_id,
                description=step.description,
                inputs=step.inputs,
                outputs=step.outputs,
                dependencies=step.dependencies,
                agent_type=auto_data.agent_type if auto_data else "adk_base",
                determinism_score=auto_data.determinism_score if auto_data else 0.5,
                automation_feasibility=auto_data.automation_feasibility if auto_data else 0.5,
                risk_level=risk_data.risk_level if risk_data else "LOW",
                requires_hitl=risk_data.requires_hitl or auto_data.requires_hitl if risk_data and auto_data else False,
                notes=f"Risk: {risk_data.notes if risk_data else 'N/A'} | Automation: {auto_data.notes if auto_data else 'N/A'}"
            )
            merged_steps.append(merged_step)

        # Create final summary
        automatable_count = sum(1 for s in merged_steps if s.automation_feasibility >= 0.6)
        summary = AutomationSummary(
            total_steps=len(merged_steps),
            automatable_count=automatable_count,
            agent_required_count=sum(1 for s in merged_steps if s.agent_type != "HUMAN"),
            human_required_count=sum(1 for s in merged_steps if s.agent_type == "HUMAN"),
            automation_potential=automatable_count / len(merged_steps) if merged_steps else 0.0
        )

        return WorkflowAnalysis(
            workflow_name="Analyzed Workflow",
            analysis_timestamp=datetime.now().isoformat(),
            steps=merged_steps,
            summary=summary,
            key_insights=self._extract_insights(merged_steps),
            risks_and_compliance={},
            recommended_architecture=None
        )

    def get_analysis_metrics(self) -> AnalysisMetrics:
        """Return collected metrics from last analysis"""
        return self.metrics.get_summary()
```

### 4.3 Individual Agent Structure

**Each agent follows this pattern:**

```python
class WorkflowParserAgent:
    def __init__(self, client, logger, tracer):
        self.client = client
        self.logger = logger
        self.tracer = tracer
        self.model = "gemini-2.0-flash-exp"

    def parse(self, workflow_text: str, session: Session) -> ParsedWorkflow:
        """Parse workflow text into structured steps"""
        system_prompt = AGENT1_SYSTEM_PROMPT
        user_prompt = USER_PROMPT_TEMPLATE.format(workflow=workflow_text)

        self.logger.debug(f"[{session.id}] Agent 1 calling API with {len(workflow_text)} chars")

        start_time = time.time()
        response = self.client.models.generate_content(
            model=self.model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.1,
                response_mime_type="application/json"
            )
        )
        latency = time.time() - start_time

        self.logger.debug(f"[{session.id}] Agent 1 API latency: {latency:.2f}s")
        self.metrics.record_latency("agent1", latency)

        parsed = json.loads(response.text)
        return ParsedWorkflow(**parsed)
```

### 4.4 Custom Tools Implementation

**Tool 1: lookup_api_docs**
```python
def lookup_api_docs(step_description: str) -> dict:
    """
    Look up if an API exists for the given step.

    Used by Agent 3 to determine if step is automatable.
    In production, this could query a real API database.
    For MVP, return mock data based on keywords.
    """
    api_db = {
        "email": {"api_exists": True, "api_name": "Gmail API", "determinism": 1.0},
        "database": {"api_exists": True, "api_name": "SQL API", "determinism": 1.0},
        "review": {"api_exists": False, "api_name": None, "determinism": 0.2},
        "approve": {"api_exists": False, "api_name": None, "determinism": 0.3},
    }
    # Find matching API, return result
    # Log this tool call with trace_id
```

**Tool 2: get_compliance_rules**
```python
def get_compliance_rules(risk_level: str, domain: str) -> dict:
    """
    Get compliance rules for given risk level and domain.

    Used by Agent 2 to determine HITL requirements.
    """
    compliance_db = {
        ("CRITICAL", "financial"): ["SOX", "PCI-DSS"],
        ("HIGH", "healthcare"): ["HIPAA"],
        ("MEDIUM", "general"): [],
        # ...
    }
    # Return applicable rules and HITL requirements
```

### 4.5 Session State Management

**SessionState:**
```python
@dataclass
class SessionState:
    session_id: str           # Unique session ID
    trace_id: str             # For tracing across agents
    created_at: datetime      # Session creation time
    parsed_steps: Optional[ParsedWorkflow] = None     # From Agent 1 (SEQUENTIAL)
    risks: Optional[List[RiskAssessment]] = None      # From Agent 2 (PARALLEL)
    automation: Optional[List[AutomationData]] = None # From Agent 3 (PARALLEL)
    final_analysis: Optional[WorkflowAnalysis] = None # After merge

    # Metrics tracking
    agent1_latency: Optional[float] = None
    agent2_latency: Optional[float] = None
    agent3_latency: Optional[float] = None
    parallel_start_time: Optional[datetime] = None    # When Agent 2 & 3 started
    parallel_end_time: Optional[datetime] = None      # When both completed
    tool_calls: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
```

**Key Changes for Parallel Execution:**
- `automation` field added for Agent 3 output (parallel with risks)
- `parallel_start_time` and `parallel_end_time` track parallel execution window
- Both Agent 2 & 3 write to their respective fields simultaneously
- Orchestrator merges at the end

**SessionManager:**
```python
class SessionManager:
    def create_session(self) -> SessionState:
        """Create new session with unique IDs"""
        return SessionState(
            session_id=str(uuid.uuid4()),
            trace_id=str(uuid.uuid4()),
            created_at=datetime.now()
        )

    def get_session(self, session_id: str) -> SessionState:
        """Retrieve session (for resuming if needed)"""
        # In MVP: store in memory
        # In production: store in database
        pass
```

### 4.6 Observability Implementation

**Structured Logger:**
```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.handler = logging.StreamHandler()
        self.handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(self.handler)

    def info(self, msg: str, **kwargs):
        """Log INFO with structured context"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": "INFO",
            "message": msg,
            **kwargs
        }
        self.logger.info(json.dumps(log_entry))

    def debug(self, msg: str, **kwargs):
        """Log DEBUG with structured context"""
        # Similar structure
        pass

    def error(self, msg: str, **kwargs):
        """Log ERROR with structured context"""
        # Similar structure
        pass
```

**Distributed Tracer:**
```python
from contextlib import contextmanager
from time import time

class DistributedTracer:
    def __init__(self):
        self.spans = {}  # trace_id -> list of spans

    @contextmanager
    def span(self, trace_id: str, span_id: str, operation: str):
        """Context manager for tracing a span"""
        start = time()
        try:
            yield
        finally:
            duration = time() - start
            if trace_id not in self.spans:
                self.spans[trace_id] = []
            self.spans[trace_id].append({
                "span_id": span_id,
                "operation": operation,
                "duration_ms": duration * 1000,
                "status": "success"
            })
```

**Metrics Collector:**
```python
class MetricsCollector:
    def __init__(self):
        self.counters = {}      # Event counts
        self.histograms = {}    # Latency distributions
        self.gauges = {}        # Current values

    def record_latency(self, agent: str, latency_ms: float):
        """Record agent latency"""
        key = f"agent_{agent}_latency"
        if key not in self.histograms:
            self.histograms[key] = []
        self.histograms[key].append(latency_ms)

    def record_tool_call(self, tool_name: str, duration_ms: float):
        """Record tool call"""
        key = f"tool_{tool_name}_calls"
        self.counters[key] = self.counters.get(key, 0) + 1

    def record_analysis(self, session: SessionState):
        """Record analysis metrics"""
        self.counters["analyses_total"] = self.counters.get("analyses_total", 0) + 1
        # Store latencies per agent
        if session.agent1_latency:
            self.record_latency("1_parser", session.agent1_latency)
        if session.agent2_latency:
            self.record_latency("2_risk", session.agent2_latency)
        if session.agent3_latency:
            self.record_latency("3_automation", session.agent3_latency)

    def get_summary(self) -> dict:
        """Return metrics summary"""
        return {
            "counters": self.counters,
            "histograms": self.histograms,
            "gauges": self.gauges
        }
```

### 4.7 Error Handling Strategy

```python
# Validation errors
- Empty/too-short workflow → ValueError with clear message
- Invalid JSON response → Log raw response, raise json.JSONDecodeError with trace_id
- API errors (quota, auth) → Log and propagate with trace_id
- Tool call failures → Log error, return fallback value, continue

# Logging per error type
- All errors include trace_id for correlation
- Log full context: session_id, agent_id, step_number
- Log error stack traces at DEBUG level
- Log error summary at ERROR level
```

---

## 5. Prompt Engineering Details

### 5.1 System Prompt Key Sections

**Opening:**
```
You are an expert workflow automation analyst specializing in Google ADK agents.
Your task is to analyze workflows and identify automation opportunities.
You must respond with ONLY valid JSON output.
```

**ADK Agent Types:**
```
Define each type with 1-2 sentence explanation
Include example use cases for each
Show how to choose between them
```

**Scoring Examples:**
```
Example 1: "Fetch customer record from database"
- Determinism: 1.0 (always same output for same input)
- Feasibility: 0.95 (API call, minimal error risk)
- Agent: adk_base
- Risk: LOW

Example 2: "Review email for tone and professionalism"
- Determinism: 0.3 (subjective assessment)
- Feasibility: 0.6 (LLM can help but needs human validation)
- Agent: HUMAN (or agentic_rag with HITL)
- Risk: MEDIUM
```

**JSON Schema:**
```
Include full example JSON showing:
- All fields for WorkflowStep
- AutomationSummary with realistic numbers
- Key insights as array
- Proper formatting
```

### 5.2 User Prompt Variations

**For Simple Workflows (2-3 steps):**
- Ask for explicit step breakdown
- Provide more guidance

**For Complex Workflows (8+ steps):**
- Ask agent to group into phases
- Identify critical path
- Highlight bottlenecks

---

## 6. Testing Strategy (for Phase 1.3 completion)

### 6.1 Unit Test Cases

**Test 1: Minimal Valid Input**
```
Workflow: "Step 1: Read file. Step 2: Process data. Step 3: Write output."
Expected: Valid JSON, 3 steps, automation_potential > 0.7
```

**Test 2: Complex Workflow with Dependencies**
```
Workflow: Customer support workflow with email, categorization, routing, response
Expected: Valid JSON, dependencies mapped, some HUMAN agents, HITL flags present
```

**Test 3: Edge Case - Ambiguous Workflow**
```
Workflow: Vague steps, unclear inputs/outputs
Expected: Valid JSON but with "notes" field highlighting ambiguities
```

### 6.2 Validation Checks
- JSON is valid (parses without error)
- All required Pydantic fields present
- Scores are in valid ranges (0.0-1.0)
- Agent types are from allowed set
- Risk levels are valid
- Dependencies reference valid step_ids

---

## 7. Configuration & Constants

Create `config.py`:
```python
MODEL = "gemini-2.0-flash-exp"
TEMPERATURE = 0.1  # Low for consistency
TIMEOUT = 30  # seconds
MAX_WORKFLOW_LENGTH = 10000  # characters
MIN_WORKFLOW_LENGTH = 10

# Agent types
AGENT_TYPES = ["adk_base", "agentic_rag", "TOOL", "HUMAN"]

# Risk levels
RISK_LEVELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

# Scoring boundaries
AUTOMATION_FEASIBLE_THRESHOLD = 0.6
```

---

## 8. Success Criteria for Phase 1.3

**Must Have (Core Functionality):**
- ✅ 3 sequential agents initialized successfully
- ✅ Agent 1 (Parser) extracts steps and dependencies
- ✅ Agent 2 (Risk Assessor) calls custom tool `get_compliance_rules()`
- ✅ Agent 3 (Automation Analyzer) calls custom tool `lookup_api_docs()`
- ✅ Final output is valid JSON matching Pydantic schema
- ✅ All agent outputs pass Pydantic validation

**Must Have (Session & State Management):**
- ✅ SessionManager creates unique session_id and trace_id
- ✅ State flows from Agent 1 → Agent 2 → Agent 3 via session object
- ✅ Each agent receives previous agent's output from session
- ✅ Session persists all parsed steps, risks, and final analysis

**Must Have (Observability):**
- ✅ **Logging:** Structured logs for each agent (INFO, DEBUG, ERROR levels)
- ✅ **Tracing:** Distributed trace_id passed through all 3 agents
- ✅ **Metrics:** Latency recorded per agent, tool calls counted, total analyses tracked
- ✅ Each log entry includes trace_id for correlation

**Should Have:**
- ✅ Determinism scores follow guidelines (APIs=1.0, creative=0.0-0.3)
- ✅ Automation feasibility scores reflect real constraints
- ✅ Risk levels appropriate to step type
- ✅ HITL flags set correctly based on tool output
- ✅ Key insights are actionable

**Nice to Have:**
- ✅ Retry logic for transient API errors
- ✅ Custom tool fallback values if lookup fails
- ✅ Metrics export (JSON format)

---

## 9. Blockers & Mitigations

| Blocker | Mitigation |
|---------|-----------|
| JSON response has markdown wrapper | Add "do not include markdown" to system prompt, test rigorously |
| Agent type recommendations are inconsistent | Lower temperature to 0.1, add more scoring examples |
| Sequential agents not passing state correctly | Use session.parsed_steps explicitly in Agent 2/3 prompts |
| Tool calls failing | Implement fallback values in tools, log errors clearly |
| Tracing shows wrong latencies | Ensure tracer.span() wraps entire agent method, not just API call |
| Metrics not collected | Call metrics.record_analysis() at end of orchestrator.analyze_workflow() |
| Log entries not showing trace_id | Pass trace_id to every logger call with f-string |
| API quota exceeded | Cache responses, use smaller test workflows first |

---

## 10. Implementation Roadmap

### Phase 1.3.1: Core Infrastructure (1 hour)
1. Create `session/session_state.py` - SessionState dataclass + SessionManager
2. Create `observability/logger.py` - StructuredLogger class
3. Create `observability/tracer.py` - DistributedTracer class (with span tracking)
4. Create `observability/metrics.py` - MetricsCollector class (with parallel timing)

### Phase 1.3.2: Custom Tools (30 min)
5. Create `tools/api_lookup.py` - lookup_api_docs() function (async-compatible)
6. Create `tools/compliance_checker.py` - get_compliance_rules() function (async-compatible)

### Phase 1.3.3: Individual Agents (1.5 hours)
7. Create `agents/agent1_parser.py` - WorkflowParserAgent class (SEQUENTIAL)
8. Create `agents/agent2_risk_assessor.py` - RiskAssessorAgent class (PARALLEL, async)
9. Create `agents/agent3_automation_analyzer.py` - AutomationAnalyzerAgent class (PARALLEL, async)
10. Create `prompts.py` - System prompts for all 3 agents

### Phase 1.3.4: Main Orchestrator (30 min)
11. Create `orchestrator.py` - WorkflowAnalyzerOrchestrator class
    - `analyze_workflow()` - async method with sequential + parallel flow
    - `_run_agent2()` - async wrapper for parallel execution
    - `_run_agent3()` - async wrapper for parallel execution
    - `_merge_results()` - combines risks + automation data
12. Create `config.py` - Constants and configuration
13. Create `types.py` - Pydantic models (ParsedWorkflow, RiskAssessment, AutomationData, AnalysisMetrics)

### Phase 1.3.5: Testing (1 hour)
14. Test with sample_workflows/customer_support.txt
15. Verify sequential Agent 1 runs first
16. Verify Agent 2 & 3 run in parallel (check timing)
17. Verify session state merges correctly
18. Verify logs, traces, and metrics are captured
19. Validate final JSON output against Pydantic schema

**Total Estimated Time:** 4 hours (2-3 hours + buffer for async debugging)

**Key Implementation Notes for Parallel Execution:**
- Use `asyncio.create_task()` to launch Agent 2 & 3 concurrently
- Use `asyncio.gather()` to wait for both tasks to complete
- Track parallel execution timing: `parallel_start_time` → `parallel_end_time`
- Both agents should be thread-safe (no shared mutable state)
- Merge results by matching step_id across risks and automation outputs

---

## 11. Course Requirements Coverage Summary

| Requirement | Implementation | Status |
|------------|-----------------|--------|
| **Multi-agent system** | 3 agents: Agent 1 (parser) sequential, Agent 2 & 3 (risk, automation) parallel | ✅ |
| **LLM-powered agents** | All 3 agents use gemini-2.0-flash-exp | ✅ |
| **Sequential agents** | Agent 1 runs first, output feeds to Agent 2 & 3 | ✅ |
| **Parallel agents** | Agent 2 & 3 run simultaneously via asyncio.gather() | ✅ |
| **Custom tools** | lookup_api_docs (Agent 3), get_compliance_rules (Agent 2) | ✅ |
| **Sessions & state management** | SessionManager + SessionState with trace_id, parallel timing tracking | ✅ |
| **Context engineering** | Detailed prompts with scoring examples for each agent | ✅ |
| **Logging** | StructuredLogger with INFO/DEBUG/ERROR levels, trace_id correlation | ✅ |
| **Tracing** | DistributedTracer with trace_id across all agents, parallel span tracking | ✅ |
| **Metrics** | MetricsCollector: latency per agent, parallel execution time, tool calls, totals | ✅ |

**Execution Pattern:**
```
Agent 1 (Sequential - 200ms)
    ↓
Agent 2 (Parallel - 1500ms) + Agent 3 (Parallel - 800ms) = max(1500ms) = 1500ms
    ↓
Orchestrator merges + metrics collection
    ↓
Total: ~1700ms (vs 2500ms if all sequential)

All within single trace_id for correlation across parallel execution
```

---

## Appendix: Sample Workflow for Testing

```
WORKFLOW: Customer Support Email Processing

Step 1: Receive customer email
- Input: Incoming email message
- Output: Parsed email content (from, subject, body)

Step 2: Extract key information
- Input: Email content
- Output: Extracted intent, customer ID, priority level

Step 3: Categorize request type
- Input: Extracted intent
- Output: Category (billing, technical, general)

Step 4: Check knowledge base
- Input: Category, key terms
- Output: Matching articles or solutions

Step 5: Generate draft response
- Input: Solution or escalation decision
- Output: Draft email response

Step 6: Human review
- Input: Draft response, original email
- Output: Approved/rejected response

Step 7: Send response
- Input: Approved response
- Output: Sent confirmation, ticket closed
```

**Expected Analysis:**
- Steps 1-3: adk_base (deterministic, automatable)
- Step 4: agentic_rag (knowledge retrieval, some judgment)
- Step 5: agentic_rag (LLM generation, HITL required)
- Step 6: HUMAN (judgment, quality assurance)
- Step 7: adk_base (deterministic API call)
- Automation potential: ~60% (steps 1-5 automatable, 6 human, 7 automatable)
