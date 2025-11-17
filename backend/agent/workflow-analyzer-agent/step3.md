# Step 3: Individual Agents Implementation

**Estimated Time:** 1.5 hours
**Status:** Not Started
**Goal:** Create the three specialized agents that analyze workflows

## Background

The three agents work together in this flow:
1. **Agent 1 (Parser)**: Parses workflow text into structured steps (SEQUENTIAL)
2. **Agent 2 (Risk Assessor)**: Evaluates risk for each step (PARALLEL with Agent 3)
3. **Agent 3 (Automation Analyzer)**: Determines agent types and feasibility (PARALLEL with Agent 2)

Each agent:
- Calls the Gemini API with a system prompt + user prompt
- Returns structured data (JSON-like)
- Logs its activities with trace_id
- Records latency metrics

## Tasks

### 3.1 Create System Prompts
**File:** `prompts.py`

Create three system prompts (large strings) for each agent:

**AGENT1_SYSTEM_PROMPT**
- Role: Workflow automation analyst
- Task: Parse workflow text into structured steps
- Output: JSON with array of steps containing: id, description, inputs, outputs, dependencies
- Key instruction: "You MUST respond with ONLY valid JSON, no markdown, no extra text"
- Temperature: 0.1 (low for consistency)

Example structure in prompt:
```json
{
  "steps": [
    {
      "step_id": "step_1",
      "description": "Receive customer email",
      "inputs": ["incoming email message"],
      "outputs": ["parsed email content"],
      "dependencies": []
    }
  ]
}
```

**AGENT2_SYSTEM_PROMPT**
- Role: Risk & Compliance Assessor
- Task: Evaluate risk level for each step
- Tool available: `get_compliance_rules(risk_level, domain)`
- Output: JSON with risk assessment per step
- Include scoring guidelines for risk levels (LOW, MEDIUM, HIGH, CRITICAL)
- Key instruction: "You MUST respond with ONLY valid JSON"
- Temperature: 0.1

**AGENT3_SYSTEM_PROMPT**
- Role: Automation Analyzer
- Task: Determine best agent type and scores for automation feasibility
- Tool available: `lookup_api_docs(step_description)`
- Output: JSON with agent type and scores for each step
- Include definitions of agent types: adk_base, agentic_rag, TOOL, HUMAN
- Include scoring guidelines for determinism (0.0-1.0)
- Include scoring guidelines for automation feasibility (0.0-1.0)
- Key instruction: "You MUST respond with ONLY valid JSON"
- Temperature: 0.1

### 3.2 Create Agent 1: Workflow Parser
**File:** `agents/agent1_parser.py`

Create class `WorkflowParserAgent`:

**Constructor:**
```python
def __init__(self, client, logger, tracer):
    self.client = client  # Gemini client
    self.logger = logger  # StructuredLogger instance
    self.tracer = tracer  # DistributedTracer instance
    self.model = "gemini-2.0-flash-exp"
```

**Main method:**
```python
def parse(self, workflow_text: str, session) -> list:
    """
    Parse workflow text into structured steps.

    Args:
        workflow_text: The workflow description
        session: SessionState object to store results

    Returns:
        List of ParsedStep objects

    Flow:
    1. Log that parsing started
    2. Record start time
    3. Call Gemini API with system + user prompt
    4. Parse JSON response
    5. Record latency in session and metrics
    6. Log results
    7. Return parsed steps
    """
```

**Implementation details:**
- Use Gemini's `generate_content()` with JSON response type
- Set `response_mime_type="application/json"`
- Extract response text and parse as JSON
- Handle JSON parsing errors gracefully
- Store latency in `session.agent1_latency`
- Log at INFO level: start, step count found, latency
- Log at DEBUG level: detailed step information
- Include session.trace_id in all logs

### 3.3 Create Agent 2: Risk & Compliance Assessor
**File:** `agents/agent2_risk_assessor.py`

Create class `RiskAssessorAgent`:

**Constructor:**
```python
def __init__(self, client, logger, tracer, tools):
    self.client = client
    self.logger = logger
    self.tracer = tracer
    self.tools = tools  # dict with "get_compliance_rules" function
    self.model = "gemini-2.0-flash-exp"
```

**Main method:**
```python
def assess_risk(self, session, workflow_text: str) -> list:
    """
    Assess risk for each step in the workflow.

    Args:
        session: SessionState with parsed_steps from Agent 1
        workflow_text: Original workflow text (for context)

    Returns:
        List of RiskAssessment objects

    Flow:
    1. Log that risk assessment started
    2. Record start time
    3. Create user prompt that includes:
       - Original workflow text
       - Parsed steps from session.parsed_steps
       - Instructions to call get_compliance_rules() for each step
    4. Call Gemini API with system + user prompt
    5. Parse response and handle tool calls (if any)
    6. Record latency in session and metrics
    7. Log results (risk levels, HITL flags, tool calls)
    8. Return risk assessments
    """
```

**Implementation notes:**
- This agent needs access to `session.parsed_steps` (from Agent 1)
- Include parsed steps in the user prompt so agent has context
- Tool calls: When agent calls `get_compliance_rules()`, execute it and handle result
- Store latency in `session.agent2_latency`
- Log tool calls with DEBUG level
- Include session.trace_id in all logs

### 3.4 Create Agent 3: Automation Analyzer
**File:** `agents/agent3_automation_analyzer.py`

Create class `AutomationAnalyzerAgent`:

**Constructor:**
```python
def __init__(self, client, logger, tracer, tools):
    self.client = client
    self.logger = logger
    self.tracer = tracer
    self.tools = tools  # dict with "lookup_api_docs" function
    self.model = "gemini-2.0-flash-exp"
```

**Main method:**
```python
def analyze(self, session, workflow_text: str) -> list:
    """
    Analyze automation potential for each step.

    Args:
        session: SessionState with parsed_steps and risks from Agent 1 & 2
        workflow_text: Original workflow text (for context)

    Returns:
        List of AutomationData objects

    Flow:
    1. Log that automation analysis started
    2. Record start time
    3. Create user prompt that includes:
       - Original workflow text
       - Parsed steps from session.parsed_steps
       - Risk assessments from session.risks
       - Instructions to call lookup_api_docs() for each step
    4. Call Gemini API with system + user prompt
    5. Parse response and handle tool calls
    6. Record latency in session and metrics
    7. Log results (agent types, scores, tool calls)
    8. Return automation analyses
    """
```

**Implementation notes:**
- This agent needs access to both `session.parsed_steps` and `session.risks`
- Include both in the user prompt
- Tool calls: When agent calls `lookup_api_docs()`, execute it and handle result
- Store latency in `session.agent3_latency`
- Log tool calls with DEBUG level
- Include session.trace_id in all logs
- Can run in parallel with Agent 2 (no dependency except on Agent 1)

### 3.5 Create Agents Module Init
**File:** `agents/__init__.py`

Export all three agent classes:
```python
from .agent1_parser import WorkflowParserAgent
from .agent2_risk_assessor import RiskAssessorAgent
from .agent3_automation_analyzer import AutomationAnalyzerAgent

__all__ = ["WorkflowParserAgent", "RiskAssessorAgent", "AutomationAnalyzerAgent"]
```

## Key Design Notes

1. **Tool Calling Pattern**: When an agent needs to call a tool:
   - The system prompt should instruct the agent to call it
   - The agent responds with a request to call the tool
   - The orchestrator (or agent wrapper) executes the tool
   - Results are fed back to continue the analysis

2. **JSON Output**: All agents must output valid JSON. Enforce by:
   - Setting `response_mime_type="application/json"`
   - Including "You MUST respond with ONLY valid JSON" in system prompt
   - Low temperature (0.1) for consistency

3. **Logging**: Every agent should log:
   - `[trace_id] Agent X started [operation]`
   - `[trace_id] Agent X found N [items]`
   - `[trace_id] Agent X latency: X.XXs`
   - `[trace_id] Agent X error: [error details]` (if error)

4. **State Passing**: Via session object:
   - Agent 1 writes: `session.parsed_steps`
   - Agent 2 reads: `session.parsed_steps`, writes: `session.risks`
   - Agent 3 reads: `session.parsed_steps` + `session.risks`, writes: `session.automation`

## Acceptance Criteria

- [ ] `prompts.py` created with 3 complete system prompts
- [ ] `agents/agent1_parser.py` created with WorkflowParserAgent class
- [ ] `agents/agent2_risk_assessor.py` created with RiskAssessorAgent class
- [ ] `agents/agent3_automation_analyzer.py` created with AutomationAnalyzerAgent class
- [ ] `agents/__init__.py` exports all three classes
- [ ] All agents can be instantiated without errors
- [ ] Agent 1 successfully parses workflow text (returns list of steps)
- [ ] Agent 2 successfully assesses risk (returns risk assessments)
- [ ] Agent 3 successfully analyzes automation (returns automation data)
- [ ] All agents log with trace_id included
- [ ] All agents record latency metrics
- [ ] Tool calls are properly handled and logged
- [ ] JSON responses are properly parsed (no markdown wrappers)

## Next Step

→ Once complete, move to **Step 4: Main Orchestrator Implementation**
