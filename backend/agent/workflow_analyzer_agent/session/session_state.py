"""Session state management for tracking workflow analysis sessions."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, List, Dict
import uuid


@dataclass
class SessionState:
    """
    Maintains the state of a single workflow analysis session.

    Attributes:
        session_id: Unique identifier for this analysis session
        trace_id: For distributed tracing across all agents
        created_at: Timestamp when session was created
        parsed_steps: Store Agent 1 output (workflow parsing)
        risks: Store Agent 2 output (Risk Assessment)
        automation: Store Agent 3 output (Automation Analysis)
        final_analysis: Merged final result
        agent1_latency: Agent 1 latency in milliseconds
        agent2_latency: Agent 2 latency in milliseconds
        agent3_latency: Agent 3 latency in milliseconds
        parallel_start_time: Timestamp when parallel execution started
        parallel_end_time: Timestamp when parallel execution ended
        tool_calls: List of tool calls made (for metrics)
        errors: List of errors encountered (for metrics)
    """

    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)

    # Agent outputs
    parsed_steps: Dict[str, Any] = field(default_factory=dict)
    risks: Dict[str, Any] = field(default_factory=dict)
    automation: Dict[str, Any] = field(default_factory=dict)
    final_analysis: Dict[str, Any] = field(default_factory=dict)

    # Latency metrics
    agent1_latency: float = 0.0
    agent2_latency: float = 0.0
    agent3_latency: float = 0.0

    # Parallel execution tracking
    parallel_start_time: datetime | None = None
    parallel_end_time: datetime | None = None

    # Metrics tracking
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        """Validate session state after initialization."""
        if not self.session_id:
            raise ValueError("session_id cannot be empty")
        if not self.trace_id:
            raise ValueError("trace_id cannot be empty")

    def add_tool_call(self, tool_name: str, duration_ms: float, **kwargs) -> None:
        """
        Record a tool call made during analysis.

        Args:
            tool_name: Name of the tool that was called
            duration_ms: Duration of the tool call in milliseconds
            **kwargs: Additional context about the tool call
        """
        self.tool_calls.append({
            "tool_name": tool_name,
            "duration_ms": duration_ms,
            "timestamp": datetime.utcnow(),
            **kwargs
        })

    def add_error(self, error_type: str, message: str, **kwargs) -> None:
        """
        Record an error that occurred during analysis.

        Args:
            error_type: Type of error (e.g., 'ValueError', 'TimeoutError')
            message: Error message
            **kwargs: Additional context about the error
        """
        self.errors.append({
            "error_type": error_type,
            "message": message,
            "timestamp": datetime.utcnow(),
            **kwargs
        })
