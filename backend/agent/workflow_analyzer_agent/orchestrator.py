"""Main orchestrator for workflow analysis - coordinates all agents."""
import asyncio
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini

# Load environment variables from .env file
load_dotenv()

from .session import SessionState, SessionManager
from .observability import StructuredLogger, DistributedTracer, MetricsCollector
from .agents import WorkflowParserAgent, RiskAssessorAgent, AutomationAnalyzerAgent
from .tools import lookup_api_docs, get_compliance_rules
from .types import WorkflowAnalysis, KeyInsight, AutomationSummary, WorkflowStep
from .config import MODEL


class WorkflowAnalyzerOrchestrator:
    """
    Main orchestrator for workflow analysis.

    Coordinates the execution of three specialized agents:
    1. Agent 1 (Sequential): Parses workflow into steps
    2. Agent 2 & 3 (Parallel): Risk assessment and automation analysis
    """

    def __init__(self, model: str = MODEL, workflow_repository=None):
        """
        Initialize orchestrator with all components.

        Args:
            model: Gemini model to use (default: from config)
            workflow_repository: Optional WorkflowRepository for auto-saving analysis
        """
        my_api_key = os.getenv("GOOGLE_API_KEY")
        if not my_api_key:
            raise RuntimeError("GOOGLE_API_KEY environment variable is not set")

        # Initialize ADK Gemini model and underlying Google GenAI client
        self.gemini_model = Gemini(model_name=model, api_key=my_api_key)
        # Use the underlying API client (google.genai.Client-compatible)
        self.client = self.gemini_model.api_client
        # Define a root ADK Agent for metadata and future orchestration
        self.root_agent = Agent(
            name="workflow_analysis_root",
            description="Root agent that orchestrates workflow parsing, risk, and automation analysis.",
            model=self.gemini_model,
            instruction=(
                "You analyze business workflows by coordinating parsing, "
                "risk assessment, and automation analysis steps."
            ),
            tools=[get_compliance_rules, lookup_api_docs],
        )
        self.model = model

        # Initialize core components
        self.session_manager = SessionManager()
        self.logger = StructuredLogger("WorkflowAnalyzer")
        self.tracer = DistributedTracer()
        self.metrics = MetricsCollector()

        # Initialize agents with the underlying GenAI-compatible client
        self.agent1 = WorkflowParserAgent(self.client, self.logger, self.tracer)

        tools = {
            "get_compliance_rules": get_compliance_rules,
            "lookup_api_docs": lookup_api_docs,
        }

        self.agent2 = RiskAssessorAgent(self.client, self.logger, self.tracer, tools)
        self.agent3 = AutomationAnalyzerAgent(self.client, self.logger, self.tracer, tools)

        # Optional workflow repository for auto-saving
        self.workflow_repository = workflow_repository

        self.logger.info("Orchestrator initialized successfully")

    async def analyze_workflow(self, workflow_text: str) -> WorkflowAnalysis:
        """
        Main orchestration method - sequential + parallel execution.

        Flow:
        1. Create session
        2. Run Agent 1 (sequential)
        3. Launch Agent 2 & 3 (parallel)
        4. Wait for both to complete
        5. Merge results
        6. Collect metrics
        7. Return WorkflowAnalysis

        Args:
            workflow_text: The workflow description text

        Returns:
            WorkflowAnalysis: Complete analysis result
        """
        session = self.session_manager.create_session()
        trace_id = session.trace_id

        self.logger.info(
            "Starting workflow analysis",
            trace_id=trace_id,
            workflow_length=len(workflow_text)
        )

        try:
            if not workflow_text or not isinstance(workflow_text, str):
                raise ValueError("workflow_text must be a non-empty string")

            # SEQUENTIAL: Agent 1
            self.logger.info("Agent 1: Starting workflow parsing", trace_id=trace_id)

            with self.tracer.span(trace_id, "agent1_parse", "workflow_parser"):
                steps = self.agent1.parse(workflow_text, session)

            if not steps:
                raise ValueError("Agent 1 failed to parse workflow steps")

            self.logger.info(
                "Agent 1: Completed",
                trace_id=trace_id,
                steps_found=len(steps),
                latency_ms=session.agent1_latency
            )

            # PARALLEL: Agent 2 & 3
            self.logger.info("Launching parallel agents", trace_id=trace_id)
            session.parallel_start_time = datetime.utcnow()

            task2 = asyncio.create_task(
                self._run_agent2(session, workflow_text, trace_id)
            )
            task3 = asyncio.create_task(
                self._run_agent3(session, workflow_text, trace_id)
            )

            results2, results3 = await asyncio.gather(task2, task3, return_exceptions=False)
            session.parallel_end_time = datetime.utcnow()

            self.logger.info("Parallel agents completed", trace_id=trace_id)

            # Merge results
            final_analysis = self._merge_results(session)
            session.final_analysis = final_analysis.dict()

            # Auto-save to Firestore if repository is available
            if self.workflow_repository:
                try:
                    self.workflow_repository.save_workflow_analysis(
                        workflow_id=final_analysis.workflow_id,
                        original_text=workflow_text,
                        analysis=final_analysis,
                    )
                    self.logger.info(
                        "Analysis saved successfully to Firestore",
                        trace_id=trace_id,
                        workflow_id=final_analysis.workflow_id,
                    )
                except Exception as e:
                    self.logger.warning(
                        "Failed to persist analysis to Firestore",
                        trace_id=trace_id,
                        error_type=type(e).__name__,
                        error_message=str(e),
                    )

            # Collect metrics
            self.metrics.record_analysis(session)

            self.logger.info(
                "Analysis completed successfully",
                trace_id=trace_id,
                total_steps=len(steps)
            )

            return final_analysis

        except Exception as e:
            self.logger.error(
                "Workflow analysis failed",
                trace_id=trace_id,
                error_type=type(e).__name__,
                error_message=str(e)
            )
            session.add_error(type(e).__name__, str(e), stage="orchestration")
            self.metrics.record_analysis(session)
            raise

    async def _run_agent2(self, session: SessionState, workflow_text: str, trace_id: str) -> List[Dict[str, Any]]:
        """Run Agent 2 (Risk Assessor) with tracing."""
        try:
            self.logger.info("Agent 2: Starting risk assessment", trace_id=trace_id)

            with self.tracer.span(trace_id, "agent2_risk", "risk_assessor"):
                risk_assessments = self.agent2.assess_risk(session, workflow_text)

            self.logger.info(
                "Agent 2: Completed",
                trace_id=trace_id,
                assessments_count=len(risk_assessments) if risk_assessments else 0,
                latency_ms=session.agent2_latency
            )

            return risk_assessments

        except Exception as e:
            self.logger.error(
                "Agent 2 failed",
                trace_id=trace_id,
                error_type=type(e).__name__,
                error_message=str(e)
            )
            session.add_error(type(e).__name__, str(e), agent="agent_2")
            return []

    async def _run_agent3(self, session: SessionState, workflow_text: str, trace_id: str) -> List[Dict[str, Any]]:
        """Run Agent 3 (Automation Analyzer) with tracing."""
        try:
            self.logger.info("Agent 3: Starting automation analysis", trace_id=trace_id)

            with self.tracer.span(trace_id, "agent3_automation", "automation_analyzer"):
                automation_analyses = self.agent3.analyze(session, workflow_text)

            self.logger.info(
                "Agent 3: Completed",
                trace_id=trace_id,
                analyses_count=len(automation_analyses) if automation_analyses else 0,
                latency_ms=session.agent3_latency
            )

            return automation_analyses

        except Exception as e:
            self.logger.error(
                "Agent 3 failed",
                trace_id=trace_id,
                error_type=type(e).__name__,
                error_message=str(e)
            )
            session.add_error(type(e).__name__, str(e), agent="agent_3")
            return []

    def _merge_results(self, session: SessionState) -> WorkflowAnalysis:
        """Merge results from all agents into final analysis."""
        parsed_steps = session.parsed_steps.get("steps", []) if session.parsed_steps else []
        risk_assessments = session.risks.get("risk_assessments", []) if session.risks else []
        automation_analyses = session.automation.get("automation_analyses", []) if session.automation else []

        risks_map = {r.get("step_id"): r for r in risk_assessments}
        automation_map = {a.get("step_id"): a for a in automation_analyses}

        merged_steps = []
        for step in parsed_steps:
            step_id = step.get("step_id")
            risk_data = risks_map.get(step_id, {})
            automation_data = automation_map.get(step_id, {})

            # Build suggested tools list
            suggested_tools = []
            if automation_data.get("available_api"):
                suggested_tools.append(automation_data.get("available_api"))

            # Add compliance tools if needed
            if risk_data.get("requires_human_in_loop"):
                suggested_tools.append("Human Review")

            # Add API lookup if no API found but feasible
            if not automation_data.get("available_api") and automation_data.get("automation_feasibility", 0) > 0.5:
                suggested_tools.append("Custom Integration")

            # Create WorkflowStep object
            merged_step = WorkflowStep(
                id=step_id,
                description=step.get("description", ""),
                inputs=step.get("inputs", []),
                outputs=step.get("outputs", []),
                dependencies=step.get("dependencies", []),
                agent_type=automation_data.get("recommended_agent_type", "UNKNOWN"),
                risk_level=risk_data.get("risk_level", "UNKNOWN"),
                requires_human_review=risk_data.get("requires_human_in_loop", False),
                determinism_score=automation_data.get("determinism_score", 0.0),
                automation_feasibility=automation_data.get("automation_feasibility", 0.0),
                available_api=automation_data.get("available_api"),
                suggested_tools=suggested_tools,
                mitigation_suggestions=risk_data.get("mitigation_suggestions", []),
                implementation_notes=automation_data.get("implementation_notes", ""),
            )
            merged_steps.append(merged_step)

        # Calculate summary statistics
        total_steps = len(merged_steps)
        automatable_count = sum(1 for s in merged_steps if s.automation_feasibility >= 0.6)
        agent_required_count = sum(1 for s in merged_steps if s.agent_type != "HUMAN")
        human_required_count = sum(1 for s in merged_steps if s.agent_type == "HUMAN")
        critical_risk_steps = sum(1 for s in merged_steps if s.risk_level == "CRITICAL")
        high_risk_steps = sum(1 for s in merged_steps if s.risk_level == "HIGH")

        automation_potential = automatable_count / total_steps if total_steps > 0 else 0.0

        summary = AutomationSummary(
            total_steps=total_steps,
            automatable_count=automatable_count,
            agent_required_count=agent_required_count,
            human_required_count=human_required_count,
            automation_potential=automation_potential,
            high_risk_steps=high_risk_steps,
            critical_risk_steps=critical_risk_steps
        )

        insights = self._extract_insights(merged_steps)

        final_analysis = WorkflowAnalysis(
            workflow_id=f"wf_{session.session_id[:8]}",
            session_id=session.session_id,
            steps=merged_steps,
            summary=summary,
            key_insights=insights,
            risks_and_compliance={
                "high_risk_steps": high_risk_steps,
                "critical_risk_steps": critical_risk_steps,
                "human_review_required": human_required_count > 0,
            },
            recommendations=self._generate_recommendations(summary, merged_steps),
            analysis_timestamp=datetime.utcnow().isoformat(),
            analysis_duration_ms=self._calculate_total_duration(session),
        )

        return final_analysis

    def _extract_insights(self, steps: List[WorkflowStep]) -> List[KeyInsight]:
        """Extract key insights from analyzed steps."""
        insights = []

        total = len(steps)
        automatable = sum(1 for s in steps if s.automation_feasibility >= 0.6)
        critical_risk = sum(1 for s in steps if s.risk_level == "CRITICAL")
        human_required = sum(1 for s in steps if s.agent_type == "HUMAN")

        if automatable > 0:
            automation_percentage = (automatable / total) * 100
            insights.append(KeyInsight(
                title="Strong Automation Potential",
                description=f"{automatable}/{total} steps ({automation_percentage:.0f}%) can be automated",
                priority="HIGH" if automation_percentage >= 70 else "MEDIUM",
                affected_steps=[s.id for s in steps if s.automation_feasibility >= 0.6]
            ))

        if critical_risk > 0:
            insights.append(KeyInsight(
                title="Critical Compliance Risks Detected",
                description=f"{critical_risk} step(s) marked as CRITICAL risk level",
                priority="CRITICAL",
                affected_steps=[s.id for s in steps if s.risk_level == "CRITICAL"]
            ))

        if human_required > 0:
            human_percentage = (human_required / total) * 100
            insights.append(KeyInsight(
                title="Manual Review Bottleneck",
                description=f"{human_required}/{total} steps ({human_percentage:.0f}%) require human review",
                priority="HIGH" if human_percentage > 30 else "MEDIUM",
                affected_steps=[s.id for s in steps if s.agent_type == "HUMAN"]
            ))

        return insights[:5]

    def _generate_recommendations(self, summary: AutomationSummary, steps: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        if summary.automation_potential >= 0.7:
            recommendations.append(
                f"Prioritize automation of {summary.automatable_count} automatable steps"
            )
        elif summary.automation_potential > 0:
            recommendations.append(
                f"Review the {summary.automatable_count} automatable steps for ROI"
            )

        if summary.critical_risk_steps > 0:
            recommendations.append(
                f"Implement compliance controls for {summary.critical_risk_steps} critical-risk step(s)"
            )

        if summary.human_required_count > 0:
            recommendations.append(
                f"Allocate resources for {summary.human_required_count} manual review/approval step(s)"
            )

        return recommendations

    def _calculate_total_duration(self, session: SessionState) -> float:
        """Calculate total analysis duration in milliseconds."""
        if session.parallel_start_time and session.parallel_end_time:
            parallel_duration = (session.parallel_end_time - session.parallel_start_time).total_seconds() * 1000
            total = session.agent1_latency + parallel_duration
        else:
            total = session.agent1_latency + session.agent2_latency + session.agent3_latency
        return total

    def get_analysis_metrics(self) -> Dict[str, Any]:
        """Get metrics from the analysis."""
        return self.metrics.get_summary()
