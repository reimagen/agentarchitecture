"""Metrics collection and aggregation module."""
from collections import defaultdict
from typing import Any, Dict, List
from datetime import datetime


class MetricsCollector:
    """
    Collects and aggregates metrics from workflow analysis.

    Tracks:
    - Agent latencies
    - Tool call counts and durations
    - Overall analysis metrics
    """

    def __init__(self):
        """Initialize metrics collector."""
        self.analyses_total = 0
        self.agent_1_parser_latency: List[float] = []
        self.agent_2_risk_latency: List[float] = []
        self.agent_3_automation_latency: List[float] = []
        self.tool_calls: Dict[str, List[float]] = defaultdict(list)

    def record_latency(self, agent: str, latency_ms: float) -> None:
        """
        Record latency for an agent.

        Args:
            agent: Agent identifier (e.g., 'agent_1', 'agent_2', 'agent_3')
            latency_ms: Latency in milliseconds
        """
        if latency_ms < 0:
            raise ValueError("Latency cannot be negative")

        if agent == "agent_1":
            self.agent_1_parser_latency.append(latency_ms)
        elif agent == "agent_2":
            self.agent_2_risk_latency.append(latency_ms)
        elif agent == "agent_3":
            self.agent_3_automation_latency.append(latency_ms)
        else:
            raise ValueError(f"Unknown agent: {agent}")

    def record_tool_call(self, tool_name: str, duration_ms: float) -> None:
        """
        Record a tool call.

        Args:
            tool_name: Name of the tool (e.g., 'api_lookup', 'compliance_checker')
            duration_ms: Duration of the call in milliseconds
        """
        if duration_ms < 0:
            raise ValueError("Duration cannot be negative")

        self.tool_calls[tool_name].append(duration_ms)

    def record_analysis(self, session: Any) -> None:
        """
        Record metrics for a completed analysis.

        Args:
            session: SessionState object containing analysis metrics
        """
        self.analyses_total += 1

        # Record agent latencies
        if session.agent1_latency > 0:
            self.record_latency("agent_1", session.agent1_latency)
        if session.agent2_latency > 0:
            self.record_latency("agent_2", session.agent2_latency)
        if session.agent3_latency > 0:
            self.record_latency("agent_3", session.agent3_latency)

        # Record tool calls from session
        for tool_call in session.tool_calls:
            if "tool_name" in tool_call and "duration_ms" in tool_call:
                self.record_tool_call(tool_call["tool_name"], tool_call["duration_ms"])

    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all collected metrics.

        Returns:
            Dictionary with aggregated metrics
        """
        def calculate_stats(values: List[float]) -> Dict[str, float]:
            """Calculate min, max, avg, median for a list of values."""
            if not values:
                return {
                    "count": 0,
                    "min": 0.0,
                    "max": 0.0,
                    "avg": 0.0,
                    "total": 0.0,
                }

            sorted_values = sorted(values)
            return {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values),
                "total": sum(values),
                "median": sorted_values[len(sorted_values) // 2],
            }

        # Calculate tool call metrics
        tool_metrics = {}
        for tool_name, durations in self.tool_calls.items():
            tool_metrics[tool_name] = {
                "call_count": len(durations),
                "total_duration_ms": sum(durations),
                "avg_duration_ms": sum(durations) / len(durations) if durations else 0,
            }

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "analyses_total": self.analyses_total,
            "agent_1_parser_latency": calculate_stats(self.agent_1_parser_latency),
            "agent_2_risk_latency": calculate_stats(self.agent_2_risk_latency),
            "agent_3_automation_latency": calculate_stats(self.agent_3_automation_latency),
            "tool_api_lookup_calls": tool_metrics.get("api_lookup", {"call_count": 0}),
            "tool_compliance_calls": tool_metrics.get("compliance_checker", {"call_count": 0}),
            "all_tool_calls": tool_metrics,
        }

    def reset(self) -> None:
        """Reset all metrics to initial state."""
        self.analyses_total = 0
        self.agent_1_parser_latency.clear()
        self.agent_2_risk_latency.clear()
        self.agent_3_automation_latency.clear()
        self.tool_calls.clear()
