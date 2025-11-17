"""Workflow Analyzer Agent - Multi-agent system for analyzing and automating workflows."""

from .config import (
    MODEL,
    TEMPERATURE,
    TIMEOUT,
    MAX_WORKFLOW_LENGTH,
    MIN_WORKFLOW_LENGTH,
    AGENT_TYPES,
    RISK_LEVELS,
    AUTOMATION_FEASIBLE_THRESHOLD,
)
from .session import SessionState, SessionManager
from .observability import StructuredLogger, DistributedTracer, MetricsCollector
from .types import (
    WorkflowStep,
    ParsedWorkflow,
    RiskAssessment,
    AutomationData,
    AutomationSummary,
    KeyInsight,
    WorkflowAnalysis,
    AnalysisMetrics,
)

__all__ = [
    # Config
    "MODEL",
    "TEMPERATURE",
    "TIMEOUT",
    "MAX_WORKFLOW_LENGTH",
    "MIN_WORKFLOW_LENGTH",
    "AGENT_TYPES",
    "RISK_LEVELS",
    "AUTOMATION_FEASIBLE_THRESHOLD",
    # Session
    "SessionState",
    "SessionManager",
    # Observability
    "StructuredLogger",
    "DistributedTracer",
    "MetricsCollector",
    # Types
    "WorkflowStep",
    "ParsedWorkflow",
    "RiskAssessment",
    "AutomationData",
    "AutomationSummary",
    "KeyInsight",
    "WorkflowAnalysis",
    "AnalysisMetrics",
]

__version__ = "0.1.0"
