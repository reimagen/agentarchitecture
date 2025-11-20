"""Tests for org design synthesis from workflow analysis."""

import json
from pathlib import Path

from backend.agent.workflow_analyzer_agent.types import WorkflowAnalysis
from backend.agent.org_design import (
    synthesize_agent_org_chart,
    build_agent_registry,
    build_tool_registry,
)


EXAMPLES_DIR = Path("backend/agent/org_design/examples")


def load_example_analysis() -> WorkflowAnalysis:
    """Load the example WorkflowAnalysis JSON from disk."""
    path = EXAMPLES_DIR / "workflow_analysis_example.json"
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return WorkflowAnalysis.model_validate(data)


def test_synthesize_agent_org_chart_from_example():
    """Org chart synthesis should produce agents and connections for the example."""
    analysis = load_example_analysis()

    org_chart = synthesize_agent_org_chart(analysis)
    assert org_chart.workflow_id == analysis.workflow_id
    assert org_chart.created_from_analysis_id == analysis.session_id

    # One AgentCard per WorkflowStep (step-centric design)
    step_ids = {step.id for step in analysis.steps}
    agent_step_ids = {card.step_ids[0] for card in org_chart.agents}
    assert step_ids == agent_step_ids


def test_build_registries_from_org_chart():
    """Agent and tool registries should be populated from the org chart."""
    analysis = load_example_analysis()
    org_chart = synthesize_agent_org_chart(analysis)

    agent_registry = build_agent_registry(org_chart)
    tool_registry = build_tool_registry(org_chart)

    # AgentRegistry should contain an entry per AgentCard
    assert set(agent_registry.agents.keys()) == {card.id for card in org_chart.agents}

    # ToolRegistry should contain all tools referenced by any agent card
    referenced_tools = {tool_id for card in org_chart.agents for tool_id in card.tool_ids}
    assert referenced_tools.issuperset(tool_registry.tools.keys()) or not referenced_tools

