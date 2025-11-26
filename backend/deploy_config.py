"""
Agent Engine Deployment Configuration

This file configures the WorkflowAnalyzerOrchestrator for deployment to Google Cloud's Agent Engine.
"""

import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()


class DeploymentConfig:
    """Configuration for Agent Engine deployment."""

    # Google Cloud Project Settings
    PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "")
    LOCATION: str = os.getenv("GCP_LOCATION", "us-central1")

    # Staging bucket for Agent Engine deployment
    STAGING_BUCKET: str = os.getenv("GCS_STAGING_BUCKET", "")

    # Agent Configuration
    AGENT_NAME: str = "workflow-analyzer"
    AGENT_DESCRIPTION: str = "Multi-agent system for analyzing workflows and automations"
    AGENT_DISPLAY_NAME: str = "Workflow Analyzer Agent"

    # Model Configuration
    MODEL: str = os.getenv("LLM_MODEL", "gemini-2.0-flash-exp")

    # Enable Tracing
    ENABLE_TRACING: bool = True

    # Firebase/Firestore
    FIRESTORE_DATABASE: str = os.getenv("FIRESTORE_DATABASE", "(default)")
    FIRESTORE_COLLECTION: str = os.getenv("FIREBASE_COLLECTION_WORKFLOWS", "workflows")

    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration."""
        errors = []

        if not cls.PROJECT_ID:
            errors.append("GCP_PROJECT_ID not set")
        if not cls.STAGING_BUCKET:
            errors.append("GCS_STAGING_BUCKET not set")

        if errors:
            print("Configuration validation failed:")
            for error in errors:
                print(f"  - {error}")
            return False

        return True

    @classmethod
    def to_dict(cls) -> dict:
        """Return configuration as dictionary."""
        return {
            "project_id": cls.PROJECT_ID,
            "location": cls.LOCATION,
            "staging_bucket": cls.STAGING_BUCKET,
            "agent_name": cls.AGENT_NAME,
            "agent_description": cls.AGENT_DESCRIPTION,
            "agent_display_name": cls.AGENT_DISPLAY_NAME,
            "model": cls.MODEL,
            "enable_tracing": cls.ENABLE_TRACING,
            "firestore_database": cls.FIRESTORE_DATABASE,
            "firestore_collection": cls.FIRESTORE_COLLECTION,
        }
