"""Type definitions for agent org charts and registries."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SafetyConstraints(BaseModel):
    """Structured safety and policy constraints for an agent."""

    requires_human_approval: bool = False
    restricts_pii: bool = False
    max_cost_usd: Optional[float] = None
    max_latency_ms: Optional[int] = None
    notes: Optional[str] = None
    extra: Dict[str, Any] = Field(default_factory=dict)


class AgentCard(BaseModel):
    """Logical definition of an agent for a user's workflow."""

    id: str
    name: str
    description: str
    mode: str = Field(
        default="LLM_WITH_TOOLS",
        description="Execution mode: HUMAN, LLM_WITH_TOOLS, TOOL_ONLY, or HYBRID.",
    )
    capabilities: List[str] = Field(
        default_factory=list,
        description="High-level capabilities (e.g., 'extract_invoice_data', 'route_approvals').",
    )
    data_domains: List[str] = Field(
        default_factory=list,
        description="Data domains this agent touches (e.g., 'HR', 'Finance', 'PII').",
    )
    step_ids: List[str] = Field(
        default_factory=list,
        description="Workflow step IDs this agent is responsible for.",
    )
    tool_ids: List[str] = Field(
        default_factory=list,
        description="IDs of tools from the ToolRegistry this agent can use.",
    )
    input_schema: Dict[str, Any] = Field(
        default_factory=dict,
        description="Loose schema for expected inputs (can be refined later).",
    )
    output_schema: Dict[str, Any] = Field(
        default_factory=dict,
        description="Loose schema for expected outputs (can be refined later).",
    )
    safety_constraints: SafetyConstraints = Field(
        default_factory=SafetyConstraints,
        description="Structured constraints and guardrails for this agent.",
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentConnection(BaseModel):
    """Directed connection between two agents in the org chart."""

    from_agent_id: str
    to_agent_id: str
    description: Optional[str] = None
    payload_schema: Dict[str, Any] = Field(
        default_factory=dict,
        description="Schema for the payload flowing between agents (A2A alignment).",
    )
    channel: Optional[str] = Field(
        default=None,
        description="Optional channel/type (e.g., request/response, event, notification).",
    )


class AgentOrgChart(BaseModel):
    """High-level org chart describing agents for a specific workflow."""

    workflow_id: str
    agents: List[AgentCard] = Field(default_factory=list)
    connections: List[AgentConnection] = Field(default_factory=list)
    created_from_analysis_id: Optional[str] = Field(
        default=None,
        description="Session or analysis identifier this org chart was derived from.",
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ToolRegistryEntry(BaseModel):
    """Single tool definition in the tool registry."""

    tool_id: str
    name: str
    description: str
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ToolRegistry(BaseModel):
    """Registry of tools referenced by AgentCards."""

    tools: Dict[str, ToolRegistryEntry] = Field(default_factory=dict)


class AgentRegistry(BaseModel):
    """Registry of agent cards, independent of runtime implementation."""

    agents: Dict[str, AgentCard] = Field(default_factory=dict)
