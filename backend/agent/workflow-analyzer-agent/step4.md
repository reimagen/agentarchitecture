# Step 4: Main Orchestrator Implementation

**Estimated Time:** 30 minutes
**Status:** Not Started
**Goal:** Create the main orchestrator that coordinates all agents in sequential + parallel execution

## Background

The orchestrator is the main entry point that:
1. Creates a session with unique trace_id
2. Runs Agent 1 (SEQUENTIAL) - must complete first
3. Launches Agent 2 & 3 (PARALLEL) - both run simultaneously
4. Waits for Agent 2 & 3 to complete
5. Merges results into final WorkflowAnalysis
6. Collects metrics and returns JSON output

## Tasks

### 4.1 Create Main Orchestrator Class
**File:** `orchestrator.py`

Create class `WorkflowAnalyzerOrchestrator`:

**Constructor:**
```python
def __init__(self, model: str = "gemini-2.0-flash-exp"):
    """
    Initialize orchestrator with all components.

    Args:
        model: Gemini model to use (default: "gemini-2.0-flash-exp")

    Initialize:
    - Gemini client (use genai.Client())
    - SessionManager
    - StructuredLogger
    - DistributedTracer
    - MetricsCollector
    - All 3 agents (with client, logger, tracer, and tools passed in)
    """
```

**Main async method:**
```python
async def analyze_workflow(self, workflow_text: str) -> WorkflowAnalysis:
    """
    Main orchestration method - sequential + parallel flow.

    Args:
        workflow_text: The workflow description text

    Returns:
        WorkflowAnalysis: Complete JSON analysis

    Flow:
    1. Create session with unique session_id and trace_id
    2. Log: "Starting workflow analysis" with trace_id
    3. [SEQUENTIAL] Run Agent 1:
       - Use tracer.span() context manager
       - Call agent1.parse(workflow_text, session)
       - Store result in session.parsed_steps
       - Log: steps found, latency
    4. [PARALLEL] Create tasks for Agent 2 & 3:
       - Use asyncio.create_task() for each
       - Record parallel_start_time
    5. Wait for both agents using asyncio.gather():
       - Store results in session.risks and session.automation
       - Record parallel_end_time
       - Log: both agents completed
    6. Merge results:
       - Call _merge_results(session)
       - Store in session.final_analysis
    7. Collect metrics:
       - Call metrics.record_analysis(session)
    8. Return final_analysis
    9. On error: log error with trace_id, record in metrics, raise exception
    """
```

**Helper method 1:**
```python
async def _run_agent2(self, session, workflow_text: str, trace_id: str):
    """
    Run Agent 2 (Risk Assessor) with tracing and error handling.

    Args:
        session: SessionState object
        workflow_text: Original workflow text
        trace_id: For distributed tracing

    Returns:
        List of RiskAssessment objects
    """
```

**Helper method 2:**
```python
async def _run_agent3(self, session, workflow_text: str, trace_id: str):
    """
    Run Agent 3 (Automation Analyzer) with tracing and error handling.

    Args:
        session: SessionState object
        workflow_text: Original workflow text
        trace_id: For distributed tracing

    Returns:
        List of AutomationData objects
    """
```

**Helper method 3:**
```python
def _merge_results(self, session) -> WorkflowAnalysis:
    """
    Merge results from Agent 2 (risks) and Agent 3 (automation).

    Args:
        session: SessionState with all agent outputs

    Returns:
        WorkflowAnalysis: Final merged analysis

    Logic:
    1. For each step in session.parsed_steps:
       - Find matching risk assessment in session.risks
       - Find matching automation analysis in session.automation
       - Merge all fields into single WorkflowStep
    2. Calculate summary statistics:
       - total_steps: count of all steps
       - automatable_count: steps with automation_feasibility >= 0.6
       - agent_required_count: steps where agent_type != "HUMAN"
       - human_required_count: steps where agent_type == "HUMAN"
       - automation_potential: automatable_count / total_steps
    3. Extract key insights (call _extract_insights)
    4. Return WorkflowAnalysis with all fields populated
    """
```

**Helper method 4:**
```python
def _extract_insights(self, steps: list) -> list:
    """
    Extract key insights from analyzed steps.

    Args:
        steps: List of merged WorkflowStep objects

    Returns:
        List of insight strings (2-5 findings)

    Logic:
    - Identify patterns (e.g., high-risk steps, bottlenecks)
    - Find opportunities (e.g., high automation potential areas)
    - Flag constraints (e.g., many HUMAN-required steps)
    - Suggest improvements

    Examples:
    - "60% of steps can be automated"
    - "Critical compliance requirements on 2 steps"
    - "Bottleneck at manual review step 4"
    """
```

**Getter method:**
```python
def get_analysis_metrics(self) -> dict:
    """
    Get metrics from last analysis.

    Returns:
        Dict with all collected metrics
    """
```

### 4.2 Create Usage Entry Point
**File:** `main.py` (or `__main__.py`)

Create a simple entry point for testing:

```python
import asyncio
from orchestrator import WorkflowAnalyzerOrchestrator

async def main():
    # Example workflow
    workflow_text = """
    Step 1: Receive customer email
    Step 2: Extract key information
    Step 3: Categorize request
    Step 4: Check knowledge base
    Step 5: Generate response
    Step 6: Human review
    Step 7: Send response
    """

    # Initialize and run
    orchestrator = WorkflowAnalyzerOrchestrator()
    result = await orchestrator.analyze_workflow(workflow_text)

    # Print results
    print(result)
    print(orchestrator.get_analysis_metrics())

if __name__ == "__main__":
    asyncio.run(main())
```

### 4.3 Implementation Notes

**Async Pattern:**
- Use `async def analyze_workflow()` - must be async for parallel execution
- Use `asyncio.create_task()` to launch Agent 2 & 3 concurrently
- Use `await asyncio.gather()` to wait for both to complete
- Store timing: `parallel_start_time` and `parallel_end_time`

**Error Handling:**
- Wrap entire flow in try/except
- Log errors with trace_id at ERROR level
- Record errors in metrics
- Raise exception after cleanup

**Logging Pattern:**
```python
self.logger.info(f"[{trace_id}] Agent 1 started parsing workflow")
self.logger.debug(f"[{trace_id}] Found {step_count} steps")
self.logger.error(f"[{trace_id}] Analysis failed: {str(e)}")
```

**Tracing Pattern:**
```python
with self.tracer.span(trace_id, "agent1_parse", "workflow_parser"):
    # Agent work here
    pass
```

**Metrics Recording:**
```python
self.metrics.record_analysis(session)
# Metrics collector will extract latencies from session fields
```

## Execution Flow Diagram

```
analyze_workflow() called
    ↓
Create session + trace_id
    ↓
[SEQUENTIAL] Agent 1 parse
    ↓
[PARALLEL] Launch Agent 2 & 3 tasks
    ↓
asyncio.gather() waits for both
    ↓
Merge results
    ↓
Collect metrics
    ↓
Return WorkflowAnalysis JSON
```

## Acceptance Criteria

- [ ] `orchestrator.py` created with WorkflowAnalyzerOrchestrator class
- [ ] Constructor initializes all components correctly
- [ ] `analyze_workflow()` is async method
- [ ] Agent 1 runs sequentially first
- [ ] Agent 2 & 3 launch in parallel using asyncio.create_task()
- [ ] `asyncio.gather()` properly waits for both agents
- [ ] Results are merged correctly via `_merge_results()`
- [ ] Session state flows correctly through all agents
- [ ] Logging includes trace_id in all messages
- [ ] Metrics are collected at end of analysis
- [ ] Error handling catches and logs all exceptions
- [ ] Can run with: `python -m orchestrator` or `asyncio.run(orchestrator.analyze_workflow(text))`
- [ ] Returns WorkflowAnalysis JSON object with all fields
- [ ] `get_analysis_metrics()` returns collected metrics

## Testing Before Next Step

Quick manual test:
```python
import asyncio
from orchestrator import WorkflowAnalyzerOrchestrator

async def test():
    orch = WorkflowAnalyzerOrchestrator()
    result = await orch.analyze_workflow("Step 1: Read file. Step 2: Process data. Step 3: Write output.")
    print(result)

asyncio.run(test())
```

Expected output: Valid WorkflowAnalysis JSON with 3 steps, automation potential > 0.7

## Next Step

→ Once complete, move to **Step 5: Testing & Validation**
