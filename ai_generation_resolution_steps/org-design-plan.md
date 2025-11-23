# Agent Org Design Plan (AgentOrgChart)

## Trigger Conditions

- Org design **only runs after** a workflow has been:
  - Fully analyzed by the Workflow Analyzer Orchestrator, **and**
  - Available as a JSON `WorkflowAnalysis` output (the "scoring table").
- The user must have **reviewed and approved** this scoring table before org design is invoked.
- In code, org design is entered via:
  - `run_org_design_for_analysis(analysis: WorkflowAnalysis)` in `backend/agent/org_design/service.py`.

## Inputs

- Primary input: approved `WorkflowAnalysis` (in-memory or JSON), including:
  - `steps: List[WorkflowStep]`
    - `id`, `description`, `inputs`, `outputs`, `dependencies`
    - `agent_type`, `automation_feasibility`, `requires_human_review`
    - `risk_level`, `available_api`, `suggested_tools`, `implementation_notes`, `metadata`
  - `summary: AutomationSummary`
  - `key_insights`, `risks_and_compliance`, `recommendations`
- Optionally: user overrides (e.g., tweaks to feasibility, grouping, or required human review) applied before calling org design.

## Outputs

- `AgentOrgChart`
  - `workflow_id`
  - `agents: List[AgentCard]`
  - `connections: List[AgentConnection]`
  - `created_from_analysis_id` (e.g., `session_id` or analysis version)
  - `metadata` (includes `summary` via `model_dump()`)
- `AgentRegistry`
  - `agents: Dict[str, AgentCard]` keyed by `AgentCard.id`
- `ToolRegistry`
  - `tools: Dict[str, ToolRegistryEntry]` keyed by `tool_id`

> Persistence of these outputs (e.g., saving JSON to a database keyed by `workflow_id`) is intentionally left to the application layer. The org design module is persistence-agnostic.

## Design Principles

- **Step-centric grouping**:
  - Org design groups agents **by workflow step**, not by internal implementation details.
  - Organizations primarily care **where** a workflow can be automated (per step), and which steps remain manual or human-in-the-loop.
  - For v1, default mapping is **one AgentCard per workflow step**, with room to later group multiple steps into a single agent if they are strongly coupled.

- **Backend-agnostic specs**:
  - `AgentCard` is a logical design artifact, **not** tied to any particular runtime (ADK Agent, custom Python class, or human-only step).
  - Later decisions about promoting sub-agents to ADK `Agent` objects are handled by a separate adapter layer, not by the org design types.

- **Structured safety and capabilities**:
  - `AgentCard.safety_constraints` is a `SafetyConstraints` model with fields such as:
    - `requires_human_approval`, `restricts_pii`, `max_cost_usd`, `max_latency_ms`, `notes`.
  - `AgentCard.capabilities` and `AgentCard.data_domains` provide high-level descriptors aligned with ADK/A2A best practices.
  - `AgentConnection.payload_schema` and `AgentConnection.channel` provide a basic contract for agent-to-agent exchanges.

- **Post-approval only**:
  - No org design occurs at raw input time.
  - Org design is a **second-phase artifact** produced only after the user is satisfied with the scoring table and its attributes (risk, feasibility, agent_type, tools).

## High-Level Flow

1. **Workflow analyzed**
   - Orchestrator runs and produces `WorkflowAnalysis`.
   - JSON/structured output is presented to the user as the scoring table.

2. **User approval**
   - User reviews the scoring table (JSON view).
   - User may adjust values (e.g., risk level, feasibility, required human review).
   - Once approved, the system treats this `WorkflowAnalysis` as the source of truth and calls the org design service.

3. **Org design entry point**
   - Application code calls:
     - `run_org_design_for_analysis(analysis: WorkflowAnalysis)`
   - Internally this:
     - Calls `synthesize_agent_org_chart(analysis)` to produce an `AgentOrgChart`.
     - Calls `build_agent_registry(org_chart)` to produce an `AgentRegistry`.
     - Calls `build_tool_registry(org_chart)` to produce a `ToolRegistry`.
   - The caller is responsible for persisting these outputs.

4. **AgentCard creation (step-centric)**
   - Implemented in `synthesize_agent_org_chart`:
   - For each `WorkflowStep`:
     - Create an `AgentCard` with:
       - `id`: derived from step id (e.g., `agent_{step.id}`)
       - `name`: step-aligned (e.g., `"Agent for {step.id}"`)
       - `description`: copied from `step.description`
       - `mode`: inferred from:
         - `requires_human_review`
         - `risk_level` (HIGH/CRITICAL)
         - `automation_feasibility`
         - `available_api`
       - `step_ids`: `[step.id]` for v1 (strict step-centric mapping)
       - `tool_ids`: derived from `available_api` and `suggested_tools`
         - `api::{available_api}` for direct APIs
         - `tool::{tool_name}` for suggested tools
       - `safety_constraints`: inferred using `SafetyConstraints` from risk and human-review flags
       - `capabilities` / `data_domains`: optional overrides from `step.metadata["capabilities"]` / `["data_domains"]`
       - `metadata`: copies through useful fields (e.g., `agent_type`, `risk_level`, `automation_feasibility`, `determinism_score`, `implementation_notes`)

5. **Connections (org chart edges)**
   - Implemented in `synthesize_agent_org_chart`:
   - Use `WorkflowStep.dependencies` to build `AgentConnection`s:
     - For each dependency `dep_id` in `step.dependencies`:
       - find agent for `dep_id` and create `AgentConnection(from_agent_id=agent_dep.id, to_agent_id=agent_step.id)`.
     - `payload_schema` is currently a simple marker:
       - `{"type": "workflow_step_output"}`
     - `channel` is set to `"request_response"` for now.
   - This yields a directed graph that mirrors the business workflow at the agent level.

6. **Registry population**
   - Implemented in `build_agent_registry` and `build_tool_registry`:
   - **AgentRegistry**
     - Insert each `AgentCard` into `AgentRegistry.agents` keyed by `AgentCard.id`.
   - **ToolRegistry**
     - For each tool reference (from `AgentCard.tool_ids`):
       - Normalize IDs:
         - `api::{name}` or `tool::{name}`, as produced by `synthesize_agent_org_chart`.
       - Create a `ToolRegistryEntry` with basic `name` and `description`.
       - Structured input/output schemas can be extended later.

7. **Adapter layer (future)**
   - Separate from these models, a runtime adapter will:
     - Map `AgentCard` → actual ADK `Agent` instances (or human/HITL flows).
     - Map `ToolRegistryEntry` → concrete tool implementations (e.g., `lookup_api_docs`, `get_compliance_rules`, or custom integrations).
   - MCP integration points (e.g., tool/resource URIs) can be added as fields on `ToolRegistryEntry` and/or `AgentCard` when needed.

## Current Implementation Status

- Implemented:
  - `AgentCard`, `AgentConnection`, `AgentOrgChart`, `ToolRegistryEntry`, `ToolRegistry`, `AgentRegistry`, `SafetyConstraints` in `types.py`.
  - `synthesize_agent_org_chart`, `build_agent_registry`, `build_tool_registry` in `designer.py`.
  - `run_org_design_for_analysis` service entry point in `service.py`.
  - Example input/output JSON files under `examples/` and tests in `backend/tests/test_org_design.py`.
- Not implemented yet:
  - Persistence of org design outputs to a real database.
  - Runtime adapter from `AgentOrgChart`/`AgentCard` to concrete ADK `Agent`s or MCP-aware runtimes.
