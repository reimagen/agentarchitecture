"""Distributed tracing module for tracking operation spans."""
import time
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, Generator, List, Optional


class Span:
    """Represents a single span in distributed tracing."""

    def __init__(self, span_id: str, operation: str, trace_id: str):
        """
        Initialize a span.

        Args:
            span_id: Unique identifier for this span
            operation: Name of the operation being traced
            trace_id: Identifier linking this span to a trace
        """
        self.span_id = span_id
        self.operation = operation
        self.trace_id = trace_id
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.duration_ms: float = 0.0
        self.status: str = "pending"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert span to dictionary representation.

        Returns:
            Dictionary with span data
        """
        return {
            "span_id": self.span_id,
            "trace_id": self.trace_id,
            "operation": self.operation,
            "duration_ms": self.duration_ms,
            "status": self.status,
            "start_time": datetime.fromtimestamp(self.start_time).isoformat() if self.start_time else None,
            "end_time": datetime.fromtimestamp(self.end_time).isoformat() if self.end_time else None,
        }


class DistributedTracer:
    """
    Tracks distributed traces across multiple operations and agents.

    Stores spans grouped by trace_id for correlation analysis.
    """

    def __init__(self):
        """Initialize the tracer with empty trace storage."""
        self._traces: Dict[str, List[Span]] = {}

    @contextmanager
    def span(
        self,
        trace_id: str,
        span_id: str,
        operation: str
    ) -> Generator[Span, None, None]:
        """
        Context manager for tracking operation spans.

        Args:
            trace_id: Trace identifier to group related spans
            span_id: Unique span identifier
            operation: Name of the operation

        Yields:
            Span object being tracked

        Example:
            with tracer.span("trace-123", "span-456", "parse_workflow"):
                # operation code here
                pass
        """
        span = Span(span_id, operation, trace_id)

        # Initialize trace list if needed
        if trace_id not in self._traces:
            self._traces[trace_id] = []

        # Record start
        span.start_time = time.time()
        span.status = "running"

        try:
            yield span
            span.status = "success"
        except Exception as e:
            span.status = f"error: {type(e).__name__}"
            raise
        finally:
            # Record end and calculate duration
            span.end_time = time.time()
            span.duration_ms = (span.end_time - span.start_time) * 1000
            self._traces[trace_id].append(span)

    def get_trace(self, trace_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all spans for a trace.

        Args:
            trace_id: The trace identifier

        Returns:
            List of span dictionaries
        """
        spans = self._traces.get(trace_id, [])
        return [span.to_dict() for span in spans]

    def get_trace_summary(self, trace_id: str) -> Dict[str, Any]:
        """
        Get summary statistics for a trace.

        Args:
            trace_id: The trace identifier

        Returns:
            Dictionary with trace summary (total duration, span count, etc.)
        """
        spans = self._traces.get(trace_id, [])
        if not spans:
            return {"trace_id": trace_id, "span_count": 0, "total_duration_ms": 0.0}

        total_duration = sum(span.duration_ms for span in spans)
        successful_spans = sum(1 for span in spans if span.status == "success")

        return {
            "trace_id": trace_id,
            "span_count": len(spans),
            "successful_spans": successful_spans,
            "total_duration_ms": total_duration,
            "operations": [span.operation for span in spans],
        }

    def clear_trace(self, trace_id: str) -> None:
        """
        Clear all spans for a trace.

        Args:
            trace_id: The trace identifier to clear
        """
        if trace_id in self._traces:
            del self._traces[trace_id]

    def clear_all(self) -> None:
        """Clear all traces from storage."""
        self._traces.clear()
