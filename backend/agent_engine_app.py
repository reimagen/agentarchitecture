"""
Agent Engine Application Wrapper

This module wraps the WorkflowAnalyzerOrchestrator for deployment to Google Cloud's Agent Engine.
It provides the required interface for Agent Engine's async_stream_query endpoint.
"""

import asyncio
import json
from typing import AsyncGenerator, Optional
from google.adk.app import AdkApp
from google.genai.types import Part, Content
from dotenv import load_dotenv

from agent.workflow_analyzer_agent.orchestrator import WorkflowAnalyzerOrchestrator
from deploy_config import DeploymentConfig

# Load environment variables
load_dotenv()


class WorkflowAnalyzerApp:
    """Agent Engine wrapper for Workflow Analyzer."""

    def __init__(self):
        """Initialize the application with deployment configuration."""
        # Validate configuration
        if not DeploymentConfig.validate():
            raise RuntimeError("Deployment configuration validation failed")

        # Initialize orchestrator
        self.orchestrator = WorkflowAnalyzerOrchestrator(
            model=DeploymentConfig.MODEL
        )

    async def async_stream_query(
        self,
        query: str,
        session_id: Optional[str] = None
    ) -> AsyncGenerator[Part, None]:
        """
        Process a workflow analysis query and stream results.

        Args:
            query: Workflow text to analyze
            session_id: Optional session ID for tracking

        Yields:
            Parts of the analysis response
        """
        try:
            # Analyze the workflow
            analysis = await self.orchestrator.analyze_workflow(
                workflow_text=query,
                workflow_name=session_id
            )

            # Yield results as streaming parts
            if analysis:
                # Convert analysis to JSON for streaming
                result_json = {
                    "success": True,
                    "analysis": {
                        "steps": [step.dict() if hasattr(step, 'dict') else step for step in analysis.get("steps", [])],
                        "risks": analysis.get("risks", []),
                        "automation_potential": analysis.get("automation_summary", {}),
                        "key_insights": analysis.get("key_insights", []),
                    }
                }

                # Stream the result
                yield Part.from_text(json.dumps(result_json, indent=2))
            else:
                yield Part.from_text(
                    json.dumps({
                        "success": False,
                        "error": "Analysis returned no results"
                    })
                )

        except Exception as e:
            # Stream error response
            yield Part.from_text(
                json.dumps({
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__
                })
            )


# Initialize the app instance for Agent Engine
_app_instance: Optional[WorkflowAnalyzerApp] = None


def get_app() -> WorkflowAnalyzerApp:
    """Get or create the app instance."""
    global _app_instance
    if _app_instance is None:
        _app_instance = WorkflowAnalyzerApp()
    return _app_instance


# Create AdkApp for Agent Engine deployment
app = AdkApp(
    app_callable=get_app,
    enable_tracing=DeploymentConfig.ENABLE_TRACING,
    enable_monitoring=True,
)
