"""Service-layer helpers for running org design after analysis approval.

These functions are intentionally persistence-agnostic: they return
AgentOrgChart and registries, and the caller is responsible for storing
them (e.g., in a database or object store) keyed by workflow_id.
"""

from typing import Tuple

from agent.workflow_analyzer_agent.types import WorkflowAnalysis

from .designer import (
    build_agent_registry,
    build_tool_registry,
    synthesize_agent_org_chart,
)
from .types import AgentOrgChart, AgentRegistry, ToolRegistry


def run_org_design_for_analysis(
    analysis: WorkflowAnalysis,
) -> Tuple[AgentOrgChart, AgentRegistry, ToolRegistry]:
    """Run org design for an approved WorkflowAnalysis.

    This should be called only after the user has reviewed and approved
    the scoring table / WorkflowAnalysis for a given workflow.

    The caller is expected to persist or otherwise handle the returned
    objects (e.g., store JSON in a database keyed by workflow_id).
    """
    org_chart = synthesize_agent_org_chart(analysis)
    agent_registry = build_agent_registry(org_chart)
    tool_registry = build_tool_registry(org_chart)

    return org_chart, agent_registry, tool_registry
