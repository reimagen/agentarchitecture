# Step 5: Testing & Validation

**Estimated Time:** 1 hour
**Status:** Not Started
**Goal:** Thoroughly test the complete system and validate all outputs

## Background

This step focuses on:
- Testing individual components
- Testing the full workflow end-to-end
- Validating JSON output format
- Verifying parallel execution timing
- Checking observability (logs, traces, metrics)

## Test Cases

### 5.1 Unit Tests for Individual Components

#### Test 1: Session Management
```
Test: Create session
Expected:
- session_id is UUID format
- trace_id is UUID format
- created_at is datetime
- All optional fields are None initially

Test: Get session
Expected:
- Retrieved session matches created session
```

#### Test 2: Observability Components
```
Test: StructuredLogger formats JSON
Expected:
- Log entry contains: timestamp, level, message, context fields
- All fields are properly JSON-serialized

Test: DistributedTracer tracks spans
Expected:
- Span contains: span_id, operation, duration_ms, status
- Spans grouped by trace_id

Test: MetricsCollector records metrics
Expected:
- Latencies stored correctly
- Tool calls incremented
- get_summary() returns all metrics
```

#### Test 3: Custom Tools
```
Test: lookup_api_docs() for known APIs
Examples:
- "send email" → {api_exists: true, api_name: "Gmail API", determinism: 1.0}
- "read from database" → {api_exists: true, api_name: "SQL API", determinism: 1.0}
- "review document" → {api_exists: false, determinism: 0.2}

Test: get_compliance_rules() for various combinations
Examples:
- ("CRITICAL", "financial") → [SOX, PCI-DSS], requires_audit=True, hitl_required=True
- ("LOW", "general") → [], requires_audit=False, hitl_required=False
- ("HIGH", "healthcare") → [HIPAA], requires_audit varies
```

### 5.2 Agent Integration Tests

#### Test 4: Agent 1 Parsing
```
Input workflow:
"Step 1: Read file
Step 2: Process data
Step 3: Write output"

Expected output:
- 3 steps parsed
- Each step has: id, description, inputs, outputs, dependencies
- Step 1 has no dependencies
- Steps 2-3 depend on previous step
- Valid JSON format
```

#### Test 5: Agent 2 Risk Assessment
```
Input: Parsed steps from Test 4

Expected output:
- Risk assessment for each step
- Each has: step_id, risk_level (LOW/MEDIUM/HIGH/CRITICAL), requires_hitl (bool), notes
- Risk levels appropriate to step type:
  - "Read file" → LOW
  - "Process data" → MEDIUM or LOW
  - "Write output" → MEDIUM
```

#### Test 6: Agent 3 Automation Analysis
```
Input: Parsed steps + risks from Tests 4-5

Expected output:
- Automation analysis for each step
- Each has: step_id, agent_type, determinism_score (0.0-1.0), automation_feasibility (0.0-1.0)
- Agent types appropriate:
  - "Read file" → adk_base
  - "Process data" → adk_base or agentic_rag
  - "Write output" → adk_base
- Scores reflect determinism (APIs → 1.0, judgment → 0.0-0.3)
```

### 5.3 End-to-End Tests

#### Test 7: Simple Workflow
```
Input:
"Step 1: Read file.
Step 2: Process data.
Step 3: Write output."

Test:
- Run full orchestrator.analyze_workflow()
- Verify output is valid JSON
- Verify all 3 steps present
- Verify automation_potential > 0.7 (mostly automatable)
- Verify no errors in logs
- Verify trace_id present in all logs
```

#### Test 8: Complex Workflow with Humans
```
Input: Customer support workflow
"Step 1: Receive email → Step 2: Extract info → Step 3: Categorize →
Step 4: Check KB → Step 5: Draft response → Step 6: Human review →
Step 7: Send email"

Test:
- Run full orchestrator
- Verify 7 steps parsed
- Verify steps 1-5 are automatable (feasibility >= 0.6)
- Verify step 6 is HUMAN agent type
- Verify step 7 is automatable
- Verify automation_potential around 0.6-0.7 (5-6 out of 7)
- Verify dependencies chain correctly
```

#### Test 9: Ambiguous/Edge Case Workflow
```
Input: Vague steps
"Step 1: Do something
Step 2: Then do another thing
Step 3: Finally, finish up"

Test:
- Run full orchestrator
- Should still produce valid JSON
- Steps should be parsed despite vagueness
- notes field should highlight ambiguities
- No crashes or errors
```

#### Test 10: Parallel Execution Timing
```
Test:
- Run orchestrator
- Measure timing:
  - sequential_time = agent1_latency
  - parallel_time = max(agent2_latency, agent3_latency)
  - total_time ≈ sequential_time + parallel_time
  - verify total_time < sequential_time + agent2_latency + agent3_latency
    (i.e., parallel saved time vs sequential)

Example:
- Agent 1: 200ms
- Agent 2: 1500ms
- Agent 3: 800ms
- If sequential: 200 + 1500 + 800 = 2500ms
- If parallel: 200 + max(1500, 800) = 1700ms ✓
```

### 5.4 Output Validation Tests

#### Test 11: JSON Schema Validation
```
Verify final WorkflowAnalysis output:
- workflow_name: string (not empty)
- analysis_timestamp: ISO format datetime
- steps: array of WorkflowStep objects
  - Each step has all required fields
  - step_id matches pattern "step_N"
  - agent_type in ["adk_base", "agentic_rag", "TOOL", "HUMAN"]
  - determinism_score in [0.0, 1.0]
  - automation_feasibility in [0.0, 1.0]
  - risk_level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
  - requires_hitl: boolean
  - dependencies: list of valid step_ids (or empty)
- summary: AutomationSummary
  - total_steps: integer
  - automatable_count: integer <= total_steps
  - agent_required_count: integer
  - human_required_count: integer
  - automation_potential: float in [0.0, 1.0]
- key_insights: array of strings (2-5 items)
- risks_and_compliance: dict (can be empty)

Test: Pydantic model validation
- Import final result as WorkflowAnalysis model
- Should not raise validation errors
```

#### Test 12: Metrics Output
```
Verify get_analysis_metrics() returns:
- counters: dict
  - "analyses_total": integer > 0
  - "tool_api_lookup_calls": integer >= 0
  - "tool_compliance_calls": integer >= 0
- histograms: dict
  - "agent_1_parser_latency": list of floats
  - "agent_2_risk_latency": list of floats
  - "agent_3_automation_latency": list of floats
- gauges: dict (can be empty)

All values should be reasonable:
- Latencies > 0
- Counts >= 0
```

### 5.5 Observability Tests

#### Test 13: Logging
```
Test: Run orchestrator and collect logs

Expected logs (in order):
1. "[trace_id] Starting workflow analysis" (INFO)
2. "[trace_id] Running Agent 1..." (INFO)
3. "[trace_id] Agent 1 found N steps" (DEBUG)
4. "[trace_id] Agent 1 latency: X.XXs" (DEBUG)
5. "[trace_id] Launching Agent 2 & 3 (PARALLEL)" (INFO)
6. "[trace_id] Running Agent 2..." (INFO)
7. "[trace_id] Running Agent 3..." (INFO)
8. "[trace_id] Tool call: get_compliance_rules" (DEBUG)
9. "[trace_id] Tool call: lookup_api_docs" (DEBUG)
10. "[trace_id] Both Agent 2 & 3 completed (PARALLEL)" (INFO)
11. "[trace_id] Merging results..." (INFO)
12. "[trace_id] Workflow analysis succeeded" (INFO)

Verify:
- All logs contain trace_id
- Timestamps are in order
- All levels are appropriate (INFO for major steps, DEBUG for details)
```

#### Test 14: Tracing
```
Test: Check distributed trace

Expected spans:
1. agent1_parse (operation: workflow_parser)
2. agent2_risk (operation: risk_assessor)
3. agent3_automation (operation: automation_analyzer)
4. merge_results (operation: result_merger)

All under same trace_id

Verify:
- All spans have duration_ms > 0
- Spans are in chronological order
- Parallel spans overlap (agent2 and agent3 start at similar time)
```

## Test Execution Plan

### Phase 1: Unit Tests (15 min)
1. Test session management
2. Test observability components
3. Test custom tools
4. Quick manual checks

### Phase 2: Agent Tests (20 min)
1. Test Agent 1 parsing
2. Test Agent 2 risk assessment
3. Test Agent 3 automation
4. Verify tool calling works

### Phase 3: End-to-End Tests (15 min)
1. Run simple workflow (Test 7)
2. Run complex workflow (Test 8)
3. Run edge case (Test 9)
4. Verify timing (Test 10)

### Phase 4: Validation (10 min)
1. Validate JSON schema (Test 11)
2. Check metrics (Test 12)
3. Review logs (Test 13)
4. Review traces (Test 14)

## Test Script Template

```python
import asyncio
import json
from orchestrator import WorkflowAnalyzerOrchestrator

async def test_simple_workflow():
    print("=== Test 7: Simple Workflow ===")
    orch = WorkflowAnalyzerOrchestrator()

    workflow = """
    Step 1: Read file
    Step 2: Process data
    Step 3: Write output
    """

    result = await orch.analyze_workflow(workflow)

    # Validate
    assert result.workflow_name
    assert len(result.steps) == 3
    assert result.summary.automation_potential > 0.7
    print(f"✓ Parsed {len(result.steps)} steps")
    print(f"✓ Automation potential: {result.summary.automation_potential}")
    print(f"✓ Automatable steps: {result.summary.automatable_count}")

    # Print metrics
    metrics = orch.get_analysis_metrics()
    print(f"✓ Metrics: {json.dumps(metrics, indent=2)}")

if __name__ == "__main__":
    asyncio.run(test_simple_workflow())
```

## Acceptance Criteria

- [ ] All 5 test phases execute successfully
- [ ] No crashes or unhandled exceptions
- [ ] All JSON outputs are valid and pass Pydantic validation
- [ ] All logs contain trace_id and are properly formatted
- [ ] All traces show correct execution order
- [ ] Parallel execution timing shows speedup vs sequential
- [ ] Metrics are collected and accurate
- [ ] Error handling works (gracefully handles bad inputs)
- [ ] Edge cases are handled (vague workflows, etc.)
- [ ] All insights are reasonable and actionable

## Troubleshooting Common Issues

| Issue | Diagnosis | Fix |
|-------|-----------|-----|
| JSON parse error | Agent returned markdown wrapper | Check system prompt has "no markdown" |
| Tool not called | Tool not in system prompt | Add explicit tool instruction to prompt |
| Inconsistent results | Temperature too high | Reduce TEMPERATURE to 0.1 |
| Missing trace_id in logs | Logger not receiving trace_id | Pass trace_id to logger.info() call |
| Parallel not executing | Using sync instead of async | Ensure use of `async def` and `await` |
| Latency not recorded | Session field not set | Set `session.agent_X_latency` before returning |

## Next Steps

After passing all tests:
1. Review implementation against original plan
2. Clean up any debug code
3. Document any assumptions or differences
4. Prepare for presentation/demo

## Success Definition

All tests pass ✓
- Valid JSON output ✓
- Correct automation scores ✓
- Proper parallelization ✓
- Complete observability ✓
- No errors or crashes ✓

You're done with Phase 1.3! 🎉
