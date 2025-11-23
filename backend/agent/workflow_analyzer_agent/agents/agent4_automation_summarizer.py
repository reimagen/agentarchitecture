"""Agent 4: Automation Summarizer - Synthesizes insights and provides actionable recommendations."""
import json
import time
from typing import List, Dict, Any

from ..prompts import AGENT4_SYSTEM_PROMPT


class AutomationSummarizerAgent:
    """
    Synthesizes insights from Agents 1-3 to produce automation summary and roadmap.

    This agent takes the parsed steps, risk assessments, and automation analyses
    from the previous agents and produces a comprehensive summary with actionable
    recommendations, quick wins, and implementation roadmap.

    Attributes:
        client: Gemini API client (google.genai.Client-compatible)
        logger: StructuredLogger instance for JSON logging
        tracer: DistributedTracer instance for distributed tracing
        model: Model to use (default: gemini-2.0-flash-exp)
    """

    def __init__(self, client, logger, tracer):
        """
        Initialize the Automation Summarizer Agent.

        Args:
            client: Gemini API client (google.genai.Client-compatible)
            logger: StructuredLogger instance
            tracer: DistributedTracer instance
        """
        self.client = client
        self.logger = logger
        self.tracer = tracer
        self.model = "gemini-2.0-flash-exp"

    def summarize(self, session) -> Dict[str, Any]:
        """
        Synthesize insights and generate automation summary.

        This method takes all prior agent outputs (stored in session) and produces
        a comprehensive summary with key blockers, quick wins, and implementation roadmap.

        Args:
            session: SessionState with all prior agent results (parsed_steps, risks, automation)

        Returns:
            Dictionary containing automation summary and recommendations

        Raises:
            ValueError: If session lacks required data from previous agents
            json.JSONDecodeError: If response is not valid JSON
        """
        # Log start
        self.logger.info(
            "Agent 4: Automation summarization started",
            trace_id=session.trace_id
        )

        # Record start time
        start_time = time.time()

        try:
            # Validate that previous agents have run
            parsed_steps = session.parsed_steps.get("steps", []) if session.parsed_steps else []
            risk_assessments = session.risks.get("risk_assessments", []) if session.risks else []
            automation_analyses = session.automation.get("automation_analyses", []) if session.automation else []

            if not parsed_steps:
                self.logger.warning(
                    "Agent 4: No parsed steps available",
                    trace_id=session.trace_id
                )
                return {}

            # Create comprehensive context for Agent 4
            parsed_steps_str = json.dumps(parsed_steps, indent=2)
            risk_assessments_str = json.dumps(risk_assessments, indent=2) if risk_assessments else "No risk assessments available"
            automation_analyses_str = json.dumps(automation_analyses, indent=2) if automation_analyses else "No automation analyses available"

            user_prompt = f"""Please synthesize the workflow analysis results and provide a comprehensive automation summary.

Parsed Steps (from Agent 1):
{parsed_steps_str}

Risk Assessments (from Agent 2):
{risk_assessments_str}

Automation Analyses (from Agent 3):
{automation_analyses_str}

Please provide a comprehensive summary that includes:
1. Overall assessment of automation feasibility
2. Key blockers preventing full automation
3. Quick wins (low effort, high impact opportunities)
4. High-priority steps that should be targeted
5. Compliance and risk mitigation strategy
6. Phased implementation roadmap
7. Success metrics to track progress

Respond with ONLY valid JSON, no markdown or explanations."""

            # Call Gemini API client with JSON response type
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    {
                        "role": "user",
                        "parts": [
                            {"text": AGENT4_SYSTEM_PROMPT},
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
            summary = parsed_response.get("summary", {})

            # Calculate latency
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000

            # Store results in session
            session.automation_summary = {"summary": summary}
            session.agent4_latency = latency_ms

            # Log success
            self.logger.info(
                "Agent 4: Automation summarization completed",
                trace_id=session.trace_id,
                automation_potential_percentage=summary.get("automation_potential_percentage", 0),
                quick_wins_count=len(summary.get("quick_wins", [])),
                latency_ms=latency_ms
            )

            # Log detailed summary information at DEBUG level
            self.logger.debug(
                "Agent 4: Summarization details",
                trace_id=session.trace_id,
                overall_assessment=summary.get("overall_assessment"),
                key_blockers=summary.get("key_blockers", []),
                estimated_automation_time=summary.get("estimated_time_to_full_automation")
            )

            return summary

        except json.JSONDecodeError as e:
            # Log error
            latency_ms = (time.time() - start_time) * 1000
            self.logger.error(
                "Agent 4: JSON parsing error",
                trace_id=session.trace_id,
                error_type="JSONDecodeError",
                error_message=str(e),
                latency_ms=latency_ms
            )
            session.add_error("JSONDecodeError", str(e), agent="agent_4")
            return {}

        except Exception as e:
            # Log unexpected error
            latency_ms = (time.time() - start_time) * 1000
            self.logger.error(
                "Agent 4: Unexpected error during summarization",
                trace_id=session.trace_id,
                error_type=type(e).__name__,
                error_message=str(e),
                latency_ms=latency_ms
            )
            session.add_error(type(e).__name__, str(e), agent="agent_4")
            return {}
