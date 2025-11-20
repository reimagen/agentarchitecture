"""Agent 3: Automation Analyzer - Determines automation potential for workflow steps."""
import json
import time
from typing import List, Dict, Any, Callable

from ..prompts import AGENT3_SYSTEM_PROMPT


class AutomationAnalyzerAgent:
    """
    Analyzes automation potential for workflow steps.

    This agent determines the best agent type and automation feasibility scores
    for each step. It can call tools to look up available APIs.

    Attributes:
        client: Gemini API client (google.genai.Client-compatible)
        logger: StructuredLogger instance for JSON logging
        tracer: DistributedTracer instance for distributed tracing
        tools: Dictionary containing available tools (lookup_api_docs)
        model: Model to use (default: gemini-2.0-flash-exp)
    """

    def __init__(self, client, logger, tracer, tools: Dict[str, Callable]):
        """
        Initialize the Automation Analyzer Agent.

        Args:
            client: Gemini API client (google.genai.Client-compatible)
            logger: StructuredLogger instance
            tracer: DistributedTracer instance
            tools: Dictionary with tool functions (e.g., lookup_api_docs)
        """
        self.client = client
        self.logger = logger
        self.tracer = tracer
        self.tools = tools
        self.model = "gemini-2.0-flash-exp"

    def analyze(self, session, workflow_text: str) -> List[Dict[str, Any]]:
        """
        Analyze automation potential for each step.

        This method evaluates which agent type is best suited for each step
        and scores the determinism and feasibility of automation. It may call
        external tools to look up available APIs.

        Args:
            session: SessionState with parsed_steps and risks from Agents 1 & 2
            workflow_text: Original workflow text (for context)

        Returns:
            List of automation analysis dictionaries

        Raises:
            ValueError: If session.parsed_steps is empty
            json.JSONDecodeError: If response is not valid JSON
        """
        # Log start
        self.logger.info(
            "Agent 3: Automation analysis started",
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
                    "Agent 3: No parsed steps available",
                    trace_id=session.trace_id
                )
                return []

            # Get risk assessments if available
            risk_assessments = session.risks.get("risk_assessments", []) if session.risks else []

            # Create user prompt with context from Agents 1 & 2
            parsed_steps_str = json.dumps(parsed_steps, indent=2)
            risk_assessments_str = json.dumps(risk_assessments, indent=2) if risk_assessments else "No risk assessments available yet"

            user_prompt = f"""Please analyze the automation potential for each step in this workflow.

Original Workflow:
{workflow_text}

Parsed Steps (from Agent 1):
{parsed_steps_str}

Risk Assessments (from Agent 2):
{risk_assessments_str}

For each step:
1. Determine the best agent type (adk_base, agentic_rag, TOOL, or HUMAN)
2. Use the lookup_api_docs tool to check if APIs exist for automation
3. Score the determinism (0.0=random, 1.0=perfectly consistent)
4. Score the automation feasibility (0.0=impossible, 1.0=fully automatable)
5. Assess complexity (LOW, MEDIUM, HIGH)
6. Provide implementation notes and risks

Respond with ONLY valid JSON, no markdown or explanations."""

            # Call Gemini API client with JSON response type
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    {
                        "role": "user",
                        "parts": [
                            {"text": AGENT3_SYSTEM_PROMPT},
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
            automation_analyses = parsed_response.get("automation_analyses", [])

            # Process tool calls if needed
            automation_analyses = self._process_automation_analyses(
                automation_analyses, session
            )

            # Calculate latency
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000

            # Store results in session
            session.automation = {"automation_analyses": automation_analyses}
            session.agent3_latency = latency_ms

            # Log success
            self.logger.info(
                "Agent 3: Automation analysis completed",
                trace_id=session.trace_id,
                analyses_count=len(automation_analyses),
                latency_ms=latency_ms
            )

            # Log detailed analysis information at DEBUG level
            for analysis in automation_analyses:
                self.logger.debug(
                    "Agent 3: Automation analysis for step",
                    trace_id=session.trace_id,
                    step_id=analysis.get("step_id"),
                    agent_type=analysis.get("recommended_agent_type"),
                    determinism=analysis.get("determinism_score"),
                    feasibility=analysis.get("automation_feasibility")
                )

            return automation_analyses

        except json.JSONDecodeError as e:
            # Log error
            latency_ms = (time.time() - start_time) * 1000
            self.logger.error(
                "Agent 3: JSON parsing error",
                trace_id=session.trace_id,
                error_type="JSONDecodeError",
                error_message=str(e),
                latency_ms=latency_ms
            )
            session.add_error("JSONDecodeError", str(e), agent="agent_3")
            return []

        except Exception as e:
            # Log unexpected error
            latency_ms = (time.time() - start_time) * 1000
            self.logger.error(
                "Agent 3: Unexpected error during automation analysis",
                trace_id=session.trace_id,
                error_type=type(e).__name__,
                error_message=str(e),
                latency_ms=latency_ms
            )
            session.add_error(type(e).__name__, str(e), agent="agent_3")
            return []

    def _process_automation_analyses(
        self,
        analyses: List[Dict[str, Any]],
        session
    ) -> List[Dict[str, Any]]:
        """
        Process automation analyses and call tools if needed.

        Args:
            analyses: List of automation analysis dictionaries
            session: SessionState for logging

        Returns:
            Processed analyses with tool results incorporated
        """
        processed = []

        for analysis in analyses:
            step_id = analysis.get("step_id")
            description = analysis.get("description", "")

            # Get description from parsed steps if not in analysis
            if not description and "parsed_steps" in session.__dict__:
                for step in session.parsed_steps.get("steps", []):
                    if step.get("step_id") == step_id:
                        description = step.get("description", "")
                        break

            # Call API lookup tool if needed
            if description and "lookup_api_docs" in self.tools:
                try:
                    # Look up available APIs
                    api_result = self.tools["lookup_api_docs"](
                        step_description=description,
                        trace_id=session.trace_id
                    )

                    self.logger.debug(
                        "Agent 3: Called lookup_api_docs tool",
                        trace_id=session.trace_id,
                        step_id=step_id,
                        api_found=api_result.get("api_exists"),
                        tool_result_status=api_result.get("lookup_status")
                    )

                    # Log tool call in session
                    session.add_tool_call(
                        "lookup_api_docs",
                        duration_ms=0,  # Already timed in tool
                        step_id=step_id,
                        api_exists=api_result.get("api_exists")
                    )

                    # Incorporate API info into analysis
                    if api_result.get("api_exists"):
                        analysis["available_api"] = api_result.get("api_name")

                except Exception as e:
                    self.logger.debug(
                        "Agent 3: Tool call failed",
                        trace_id=session.trace_id,
                        step_id=step_id,
                        tool="lookup_api_docs",
                        error=str(e)
                    )

            processed.append(analysis)

        return processed
