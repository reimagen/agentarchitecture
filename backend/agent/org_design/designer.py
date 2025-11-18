"""Functions to synthesize AgentOrgChart and registries from workflow analysis."""

from typing import List, Tuple

from ..workflow_analyzer_agent.types import WorkflowAnalysis, WorkflowStep
from .types import (
    AgentCard,
    AgentConnection,
    AgentOrgChart,
    AgentRegistry,
    SafetyConstraints,
    ToolRegistry,
    ToolRegistryEntry,
)


def _infer_mode(step: WorkflowStep) -> str:
    """Infer agent execution mode from a workflow step."""
    if step.requires_human_review or (step.risk_level in {"HIGH", "CRITICAL"}):
        return "HUMAN" if step.automation_feasibility < 0.4 else "HYBRID"

    if step.available_api:
        return "TOOL_ONLY"

    if step.automation_feasibility >= 0.6:
        return "LLM_WITH_TOOLS"

    return "HUMAN"


def _infer_safety(step: WorkflowStep) -> SafetyConstraints:
    """Infer basic safety constraints from risk and human-review flags."""
    requires_approval = step.requires_human_review or step.risk_level in {"HIGH", "CRITICAL"}
    # Simple heuristic: treat high/critical or explicit human review as PII-sensitive.
    restricts_pii = step.risk_level in {"HIGH", "CRITICAL"}

    return SafetyConstraints(
        requires_human_approval=requires_approval,
        restricts_pii=restricts_pii,
        notes=step.metadata.get("safety_notes") if step.metadata else None,
    )


def _collect_tool_ids(step: WorkflowStep) -> List[str]:
    """Create tool IDs from available_api and suggested_tools."""
    tool_ids: List[str] = []

    if step.available_api:
        tool_ids.append(f"api::{step.available_api}")

    for tool_name in step.suggested_tools:
        tool_ids.append(f"tool::{tool_name}")

    # Deduplicate while preserving order
    seen = set()
    deduped: List[str] = []
    for t in tool_ids:
        if t not in seen:
            seen.add(t)
            deduped.append(t)
    return deduped


def synthesize_agent_org_chart(analysis: WorkflowAnalysis) -> AgentOrgChart:
    """Create an AgentOrgChart from an approved WorkflowAnalysis.

    This is a pure, deterministic transformation that:
    - Creates one AgentCard per WorkflowStep (step-centric design).
    - Wires AgentConnection edges based on step dependencies.
    """
    agents: List[AgentCard] = []
    connections: List[AgentConnection] = []

    # Map from step id to agent id for building connections.
    step_to_agent: dict[str, str] = {}

    for step in analysis.steps:
        agent_id = f"agent_{step.id}"
        step_to_agent[step.id] = agent_id

        mode = _infer_mode(step)
        safety = _infer_safety(step)
        tool_ids = _collect_tool_ids(step)

        capabilities: List[str] = []
        if step.metadata.get("capabilities"):
            # Allow explicit override via metadata.
            explicit_caps = step.metadata["capabilities"]
            if isinstance(explicit_caps, list):
                capabilities.extend([str(c) for c in explicit_caps])

        data_domains: List[str] = []
        if step.metadata.get("data_domains"):
            explicit_domains = step.metadata["data_domains"]
            if isinstance(explicit_domains, list):
                data_domains.extend([str(d) for d in explicit_domains])

        agent = AgentCard(
            id=agent_id,
            name=f"Agent for {step.id}",
            description=step.description,
            mode=mode,
            capabilities=capabilities,
            data_domains=data_domains,
            step_ids=[step.id],
            tool_ids=tool_ids,
            input_schema={"inputs": step.inputs},
            output_schema={"outputs": step.outputs},
            safety_constraints=safety,
            metadata={
                "agent_type": step.agent_type,
                "risk_level": step.risk_level,
                "automation_feasibility": step.automation_feasibility,
                "determinism_score": step.determinism_score,
                "implementation_notes": step.implementation_notes,
            },
        )
        agents.append(agent)

    # Build connections based on step dependencies.
    for step in analysis.steps:
        to_agent_id = step_to_agent.get(step.id)
        if not to_agent_id:
            continue

        for dep_id in step.dependencies:
            from_agent_id = step_to_agent.get(dep_id)
            if not from_agent_id:
                continue

            connections.append(
                AgentConnection(
                    from_agent_id=from_agent_id,
                    to_agent_id=to_agent_id,
                    description=f"Output of {dep_id} feeds into {step.id}",
                    payload_schema={"type": "workflow_step_output"},
                    channel="request_response",
                )
            )

    org_chart = AgentOrgChart(
        workflow_id=analysis.workflow_id,
        agents=agents,
        connections=connections,
        created_from_analysis_id=analysis.session_id,
        metadata={
            "summary": analysis.summary.model_dump(),
        },
    )

    return org_chart


def build_agent_registry(org_chart: AgentOrgChart) -> AgentRegistry:
    """Create an AgentRegistry from an AgentOrgChart."""
    registry = AgentRegistry()
    for card in org_chart.agents:
        registry.agents[card.id] = card
    return registry


def build_tool_registry(org_chart: AgentOrgChart) -> ToolRegistry:
    """Create a ToolRegistry from an AgentOrgChart's tool references."""
    registry = ToolRegistry()

    for card in org_chart.agents:
        for tool_id in card.tool_ids:
            if tool_id in registry.tools:
                continue

            if tool_id.startswith("api::"):
                name = tool_id[len("api::") :]
                description = f"API integration for {name}"
            elif tool_id.startswith("tool::"):
                name = tool_id[len("tool::") :]
                description = f"Tool for {name}"
            else:
                name = tool_id
                description = "Tool referenced by agent card"

            registry.tools[tool_id] = ToolRegistryEntry(
                tool_id=tool_id,
                name=name,
                description=description,
            )

    return registry
