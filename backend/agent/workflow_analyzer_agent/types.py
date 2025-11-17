"""Type definitions for workflow analysis using Pydantic models."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class WorkflowStep(BaseModel):
    """Individual step in a parsed workflow."""

    id: str
    description: str
    inputs: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    agent_type: Optional[str] = None
    execution_order: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "id": "step_1",
                "description": "Parse input workflow",
                "inputs": ["workflow_text"],
                "outputs": ["parsed_steps"],
                "dependencies": [],
                "agent_type": "adk_base",
            }
        }


class ParsedWorkflow(BaseModel):
    """Complete parsed workflow with all steps."""

    steps: List[WorkflowStep]
    total_steps: int
    has_cycles: bool = False
    is_valid: bool = True
    parsing_notes: Optional[str] = None

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "steps": [],
                "total_steps": 5,
                "has_cycles": False,
                "is_valid": True,
            }
        }


class RiskAssessment(BaseModel):
    """Risk assessment for a specific workflow step."""

    step_id: str
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    requires_hitl: bool = False
    confidence_score: float = Field(ge=0.0, le=1.0)
    notes: Optional[str] = None
    mitigation_strategy: Optional[str] = None

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "step_id": "step_1",
                "risk_level": "MEDIUM",
                "requires_hitl": False,
                "confidence_score": 0.85,
            }
        }


class AutomationData(BaseModel):
    """Automation analysis for a specific workflow step."""

    step_id: str
    agent_type: str
    determinism_score: float = Field(ge=0.0, le=1.0)
    automation_feasibility: float = Field(ge=0.0, le=1.0)
    complexity_level: str  # LOW, MEDIUM, HIGH
    requires_human_review: bool = False
    notes: Optional[str] = None

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "step_id": "step_1",
                "agent_type": "adk_base",
                "determinism_score": 0.95,
                "automation_feasibility": 0.88,
                "complexity_level": "MEDIUM",
            }
        }


class AutomationSummary(BaseModel):
    """Summary statistics for automation analysis."""

    total_steps: int
    automatable_count: int
    agent_required_count: int
    human_required_count: int
    automation_potential: float = Field(ge=0.0, le=1.0)
    high_risk_steps: int = 0
    critical_risk_steps: int = 0

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "total_steps": 5,
                "automatable_count": 4,
                "agent_required_count": 3,
                "human_required_count": 2,
                "automation_potential": 0.80,
            }
        }


class KeyInsight(BaseModel):
    """Key insight from the analysis."""

    title: str
    description: str
    priority: str = "MEDIUM"  # LOW, MEDIUM, HIGH, CRITICAL
    affected_steps: List[str] = Field(default_factory=list)

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "title": "High dependency chains detected",
                "description": "Some steps have complex dependencies",
                "priority": "HIGH",
                "affected_steps": ["step_1", "step_3"],
            }
        }


class WorkflowAnalysis(BaseModel):
    """Final comprehensive workflow analysis result."""

    workflow_id: str
    session_id: str
    steps: List[WorkflowStep]
    summary: AutomationSummary
    key_insights: List[KeyInsight] = Field(default_factory=list)
    risks_and_compliance: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)
    analysis_timestamp: str
    analysis_duration_ms: float

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "workflow_id": "wf_123",
                "session_id": "session_456",
                "steps": [],
                "summary": {
                    "total_steps": 5,
                    "automatable_count": 4,
                    "agent_required_count": 3,
                    "human_required_count": 2,
                    "automation_potential": 0.80,
                },
                "key_insights": [],
                "recommendations": ["Automate step 1", "Review step 3"],
            }
        }


class AnalysisMetrics(BaseModel):
    """Metrics for a completed analysis."""

    session_id: str
    total_duration_ms: float
    agent_1_duration_ms: float
    agent_2_duration_ms: float
    agent_3_duration_ms: float
    parallel_execution_efficiency: float = Field(ge=0.0, le=1.0)
    tool_calls_total: int = 0
    errors_total: int = 0
    timestamp: str

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "session_id": "session_456",
                "total_duration_ms": 5000.0,
                "agent_1_duration_ms": 1500.0,
                "agent_2_duration_ms": 2000.0,
                "agent_3_duration_ms": 1800.0,
                "parallel_execution_efficiency": 0.85,
            }
        }
