"""Agent 2: Risk Assessor - Evaluates risk and compliance for each workflow step."""
import json
import time
from typing import List, Dict, Any, Optional, Callable

from ..prompts import AGENT2_SYSTEM_PROMPT


class RiskAssessorAgent:
    """
    Assesses risk and compliance requirements for workflow steps.

    This agent evaluates the risk level of each step and identifies applicable
    compliance requirements. It can call tools to look up compliance rules.

    Attributes:
        client: Gemini API client (google.genai.Client-compatible)
        logger: StructuredLogger instance for JSON logging
        tracer: DistributedTracer instance for distributed tracing
        tools: Dictionary containing available tools (get_compliance_rules)
        model: Model to use (default: gemini-2.0-flash-exp)
    """

    def __init__(self, client, logger, tracer, tools: Dict[str, Callable]):
        """
        Initialize the Risk Assessor Agent.

        Args:
            client: Gemini API client (google.genai.Client-compatible)
            logger: StructuredLogger instance
            tracer: DistributedTracer instance
            tools: Dictionary with tool functions (e.g., get_compliance_rules)
        """
        self.client = client
        self.logger = logger
        self.tracer = tracer
        self.tools = tools
        self.model = "gemini-2.0-flash-exp"

    def assess_risk(self, session, workflow_text: str) -> List[Dict[str, Any]]:
        """
        Assess risk for each step in the workflow.

        This method evaluates the risk level and compliance implications for
        each workflow step. It may call external tools to look up compliance rules.

        Args:
            session: SessionState with parsed_steps from Agent 1
            workflow_text: Original workflow text (for context)

        Returns:
            List of risk assessment dictionaries

        Raises:
            ValueError: If session.parsed_steps is empty
            json.JSONDecodeError: If response is not valid JSON
        """
        # Log start
        self.logger.info(
            "Agent 2: Risk assessment started",
            trace_id=session.trace_id,
            workflow_length=len(workflow_text)
        )

        # Record start time
        start_time = time.time()

        try:
            # Validate that Agent 1 has run
            parsed_steps = session.parsed_steps.get("steps", [])
            if not parsed_steps:
                self.logger.warning(
                    "Agent 2: No parsed steps available",
                    trace_id=session.trace_id
                )
                return []

            # Create user prompt with context from Agent 1
            parsed_steps_str = json.dumps(parsed_steps, indent=2)
            user_prompt = f"""Please assess the risk level for each step in this workflow.

Original Workflow:
{workflow_text}

Parsed Steps (from Agent 1):
{parsed_steps_str}

For each step:
1. Determine the risk level (LOW, MEDIUM, HIGH, CRITICAL)
2. Identify if human oversight is required
3. Use the get_compliance_rules tool to find applicable regulations
4. Provide a confidence score (0.0-1.0)
5. Suggest mitigation strategies

Respond with ONLY valid JSON, no markdown or explanations."""

            # Call Gemini API client with JSON response type
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    {
                        "role": "user",
                        "parts": [
                            {"text": AGENT2_SYSTEM_PROMPT},
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
            risk_assessments = parsed_response.get("risk_assessments", [])

            # Process tool calls if needed
            risk_assessments = self._process_risk_assessments(
                risk_assessments, session
            )

            # Calculate latency
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000

            # Store results in session
            session.risks = {"risk_assessments": risk_assessments}
            session.agent2_latency = latency_ms

            # Log success
            self.logger.info(
                "Agent 2: Risk assessment completed",
                trace_id=session.trace_id,
                assessments_count=len(risk_assessments),
                latency_ms=latency_ms
            )

            # Log detailed assessment information at DEBUG level
            for assessment in risk_assessments:
                self.logger.debug(
                    "Agent 2: Risk assessment for step",
                    trace_id=session.trace_id,
                    step_id=assessment.get("step_id"),
                    risk_level=assessment.get("risk_level"),
                    requires_hitl=assessment.get("requires_human_in_loop"),
                    confidence=assessment.get("confidence_score")
                )

            return risk_assessments

        except json.JSONDecodeError as e:
            # Log error
            latency_ms = (time.time() - start_time) * 1000
            self.logger.error(
                "Agent 2: JSON parsing error",
                trace_id=session.trace_id,
                error_type="JSONDecodeError",
                error_message=str(e),
                latency_ms=latency_ms
            )
            session.add_error("JSONDecodeError", str(e), agent="agent_2")
            return []

        except Exception as e:
            # Log unexpected error
            latency_ms = (time.time() - start_time) * 1000
            self.logger.error(
                "Agent 2: Unexpected error during risk assessment",
                trace_id=session.trace_id,
                error_type=type(e).__name__,
                error_message=str(e),
                latency_ms=latency_ms
            )
            session.add_error(type(e).__name__, str(e), agent="agent_2")
            return []

    def _process_risk_assessments(
        self,
        assessments: List[Dict[str, Any]],
        session
    ) -> List[Dict[str, Any]]:
        """
        Process risk assessments and call tools if needed.

        Args:
            assessments: List of risk assessment dictionaries
            session: SessionState for logging

        Returns:
            Processed assessments with tool results incorporated
        """
        processed = []

        for assessment in assessments:
            step_id = assessment.get("step_id")
            risk_level = assessment.get("risk_level")

            # Call compliance rules tool if needed
            if risk_level and "get_compliance_rules" in self.tools:
                try:
                    # Get compliance rules
                    compliance_result = self.tools["get_compliance_rules"](
                        risk_level=risk_level,
                        domain="general",
                        trace_id=session.trace_id
                    )

                    self.logger.debug(
                        "Agent 2: Called get_compliance_rules tool",
                        trace_id=session.trace_id,
                        step_id=step_id,
                        risk_level=risk_level,
                        tool_result_status=compliance_result.get("lookup_status")
                    )

                    # Log tool call in session
                    session.add_tool_call(
                        "get_compliance_rules",
                        duration_ms=0,  # Already timed in tool
                        step_id=step_id,
                        risk_level=risk_level
                    )

                    # Incorporate compliance rules into assessment
                    assessment["applicable_regulations"] = compliance_result.get(
                        "applicable_rules",
                        []
                    )

                except Exception as e:
                    self.logger.debug(
                        "Agent 2: Tool call failed",
                        trace_id=session.trace_id,
                        step_id=step_id,
                        tool="get_compliance_rules",
                        error=str(e)
                    )

            processed.append(assessment)

        return processed
