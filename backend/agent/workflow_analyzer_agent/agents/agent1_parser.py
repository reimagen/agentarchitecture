"""Agent 1: Workflow Parser - Parses workflow text into structured steps."""
import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..prompts import AGENT1_SYSTEM_PROMPT


class WorkflowParserAgent:
    """
    Parses workflow text into structured, actionable steps.

    This agent takes a natural language workflow description and breaks it down
    into individual steps with identified dependencies, inputs, and outputs.

    Attributes:
        client: Gemini API client (google.genai.Client-compatible)
        logger: StructuredLogger instance for JSON logging
        tracer: DistributedTracer instance for distributed tracing
        model: Model to use (default: gemini-2.0-flash-exp)
    """

    def __init__(self, client, logger, tracer):
        """
        Initialize the Workflow Parser Agent.

        Args:
            client: Gemini API client (google.genai.Client-compatible)
            logger: StructuredLogger instance
            tracer: DistributedTracer instance
        """
        self.client = client
        self.logger = logger
        self.tracer = tracer
        self.model = "gemini-2.0-flash-exp"

    def parse(self, workflow_text: str, session) -> List[Dict[str, Any]]:
        """
        Parse workflow text into structured steps.

        This method takes a workflow description and returns a list of parsed steps
        with identifiers, descriptions, inputs, outputs, and dependencies.

        Args:
            workflow_text: The workflow description text
            session: SessionState object to store results and metrics

        Returns:
            List of dictionaries representing parsed workflow steps

        Raises:
            ValueError: If workflow_text is invalid
            json.JSONDecodeError: If response is not valid JSON
        """
        # Log start
        self.logger.info(
            "Agent 1: Workflow parsing started",
            trace_id=session.trace_id,
            workflow_length=len(workflow_text)
        )

        # Record start time
        start_time = time.time()

        try:
            # Create user prompt
            user_prompt = f"""Please parse the following workflow description into structured steps:

{workflow_text}

Remember to respond with ONLY valid JSON, no markdown or explanations."""

            # Call Gemini API client with JSON response type
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    {
                        "role": "user",
                        "parts": [
                            {"text": AGENT1_SYSTEM_PROMPT},
                            {"text": user_prompt},
                        ],
                    }
                ],
                config={
                    "response_mime_type": "application/json",
                },
            )

            # Extract and parse response
            response_text = response.text.strip()

            # Handle potential markdown code blocks
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            parsed_response = json.loads(response_text)
            steps = parsed_response.get("steps", [])

            # Calculate latency
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000

            # Store results in session
            session.parsed_steps = {"steps": steps}
            session.agent1_latency = latency_ms

            # Log success
            self.logger.info(
                "Agent 1: Workflow parsing completed",
                trace_id=session.trace_id,
                steps_found=len(steps),
                latency_ms=latency_ms
            )

            # Log detailed step information at DEBUG level
            for step in steps:
                self.logger.debug(
                    "Agent 1: Parsed step",
                    trace_id=session.trace_id,
                    step_id=step.get("step_id"),
                    description=step.get("description"),
                    dependencies=step.get("dependencies", [])
                )

            return steps

        except json.JSONDecodeError as e:
            # Log error
            latency_ms = (time.time() - start_time) * 1000
            self.logger.error(
                "Agent 1: JSON parsing error",
                trace_id=session.trace_id,
                error_type="JSONDecodeError",
                error_message=str(e),
                latency_ms=latency_ms
            )
            session.add_error("JSONDecodeError", str(e), agent="agent_1")
            return []

        except Exception as e:
            # Log unexpected error
            latency_ms = (time.time() - start_time) * 1000
            self.logger.error(
                "Agent 1: Unexpected error during parsing",
                trace_id=session.trace_id,
                error_type=type(e).__name__,
                error_message=str(e),
                latency_ms=latency_ms
            )
            session.add_error(type(e).__name__, str(e), agent="agent_1")
            return []
