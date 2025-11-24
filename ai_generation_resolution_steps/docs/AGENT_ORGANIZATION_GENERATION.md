# Agent Organization Design Generation

This document outlines the process for generating the Agent Organization Chart, Agent Cards (Registry), and Tool Registries based on an approved workflow analysis. This functionality is triggered from the frontend and processed in the backend.

## Triggering Generation

The generation process is initiated when a user clicks the "Approve Workflow" button in the frontend.

## Backend Flow

1.  **Frontend Action:** The frontend (`App.js`) makes a `POST` request to `/workflows/{workflow_id}/approve`.
2.  **API Endpoint (`backend/api/approval.py`):**
    *   The `approve_workflow` endpoint receives the request.
    *   It calls `workflow_repository.approve_workflow(workflow_id, approved_by)`.
3.  **Workflow Repository (`backend/database/workflow_repository.py`):**
    *   The `approve_workflow` method first updates the `approvalStatus` to "APPROVED" in Firestore.
    *   It then calls `_trigger_org_design_synthesis(workflow_id)`.
    *   **Crucially**, `approve_workflow` then returns the updated workflow document (which now includes the generated `orgChart`, `agentRegistry`, and `toolRegistry` after `_trigger_org_design_synthesis` has completed its saving).
4.  **Org Design Synthesis (`workflow_repository.py::_trigger_org_design_synthesis`):**
    *   This internal method retrieves the `WorkflowAnalysis` object for the given `workflow_id`.
    *   It invokes `agent.org_design.service.run_org_design_for_analysis` with the `WorkflowAnalysis` object.
    *   After receiving the generated `org_chart`, `agent_registry`, and `tool_registry` from the service, it saves them to the Firestore document using `self.save_org_chart`.
    *   It returns the generated `org_chart`, `agent_registry`, and `tool_registry`.

## Generation Logic

The core generation logic resides in `backend/agent/org_design/service.py` and delegates to functions within `backend/agent/org_design/designer.py`.

### Input Data (`WorkflowAnalysis`)

The `run_org_design_for_analysis` function expects a `WorkflowAnalysis` object as input. An example of this structure is provided in `backend/agent/org_design/examples/workflow_analysis_example.json`.

**Key components of `WorkflowAnalysis` relevant to generation:**
*   `steps`: Contains detailed information about each step, including `agent_type`, `automation_feasibility`, `determinism_score`, `suggested_tools`, `inputs`, `outputs`, and `dependencies`. This information is crucial for determining agent roles, capabilities, and tool requirements.
*   `workflow_id`: Used for identification and context.

### Generation Steps (in `run_org_design_for_analysis`):

1.  **`synthesize_agent_org_chart(analysis)` (from `designer.py`):**
    *   Takes the `WorkflowAnalysis` and constructs a hierarchical `AgentOrgChart`. This chart groups individual agents, defines their relationships, and maps them to workflow steps.
    *   The logic here will likely involve:
        *   Identifying agents based on `step.agent_type`.
        *   Grouping agents based on `step.dependencies` or shared `data_domains`.
        *   Defining agent capabilities based on `step.description` and `step.outputs`.
        *   Assigning input/output schemas based on `step.inputs` and `step.outputs`.
        *   Incorporating `risk_level`, `automation_feasibility`, and `determinism_score` into agent metadata.
        *   Mapping `suggested_tools` to agent requirements.

2.  **`build_agent_registry(org_chart)` (from `designer.py`):**
    *   Takes the `AgentOrgChart` and flattens it into a `AgentRegistry`.
    *   Each entry in the registry represents a distinct agent, structured according to the `agent_card_example.json`.
    *   This involves extracting details like `id`, `name`, `description`, `mode`, `capabilities`, `data_domains`, `step_ids`, `tool_ids`, `input_schema`, `output_schema`, and `safety_constraints` for each agent defined in the `org_chart`.

3.  **`build_tool_registry(org_chart)` (from `designer.py`):**
    *   Takes the `AgentOrgChart` and extracts all unique tools required by the agents, forming a `ToolRegistry`.
    *   Each tool will have a definition that might include its `id`, `name`, `description`, `input_schema`, `output_schema`, and any specific configuration.

## Output to User (Frontend Display)

After successful generation and persistence in the backend, the updated workflow data (including `orgChart`, `agentRegistry`, and `toolRegistry`) is returned to the frontend.

### Frontend Handling (`App.js`):

1.  The `handleApproveWorkflow` function receives the full updated workflow object from the backend.
2.  It merges this new data into the `analysisResult` state, ensuring that `agentRegistry`, `orgChart`, and `toolRegistry` are available in the frontend state.
3.  **Agent Cards:**
    *   The `App.js` component conditionally renders an "Agent Cards" section if `analysisResult.agentRegistry` exists and is not empty.
    *   A `DownloadButton` component is used to allow the user to download the `analysisResult.agentRegistry` as `agent_cards.json`.
    *   **Expected JSON Format:** The downloaded JSON for agent cards should match the structure exemplified in `backend/agent/org_design/examples/agent_card_example.json`. This example shows a single agent definition, and the `agentRegistry` would be a collection (e.g., dictionary mapping agent IDs to these structures).

### Future Considerations (Org Chart & Tool Registry)

Similar download sections and buttons can be added for the `orgChart` and `toolRegistry` by following the pattern established for `agentRegistry`.

## Conclusion

The backend has robust mechanisms (`service.py`, `designer.py`) for generating these artifacts from a `WorkflowAnalysis`. The frontend is set up to receive and display (and allow download of) the `agentRegistry`. The key is ensuring the backend correctly populates `orgChart`, `agentRegistry`, and `toolRegistry` within the `WorkflowAnalysis` document in Firestore upon approval.
