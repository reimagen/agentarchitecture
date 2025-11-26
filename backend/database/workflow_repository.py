"""Firestore repository for workflow storage and retrieval."""
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.workflow_analyzer_agent.types import WorkflowAnalysis
from agent.org_design.types import AgentOrgChart, AgentRegistry, ToolRegistry
from database.exceptions import (
    WorkflowNotFoundError,
    InvalidApprovalStateError,
    FirestoreError,
    SerializationError,
)
from database.firebase_client import FirebaseClient

load_dotenv()


class WorkflowRepository:
    """Repository for managing workflow documents in Firestore."""

    def __init__(self):
        """Initialize repository with Firestore client."""
        self.db = FirebaseClient.get_db()
        self.collection_name = os.getenv("FIREBASE_COLLECTION_WORKFLOWS", "workflows")

    def save_workflow_analysis(
        self,
        workflow_id: str,
        original_text: str,
        analysis: WorkflowAnalysis,
        workflow_name: Optional[str] = None, # Added this parameter
    ) -> None:
        """
        Save workflow analysis to Firestore.
        # ...
        # (Rest of the docstring remains the same)
        """
        try:
            # Serialize analysis to dict
            analysis_dict = analysis.model_dump() if hasattr(analysis, "model_dump") else analysis.dict()

            now = datetime.utcnow().isoformat() + "Z"

            # Check if document exists to preserve createdAt
            doc_ref = self.db.collection(self.collection_name).document(workflow_id)
            doc = doc_ref.get()

            document_data = {
                "originalText": original_text,
                "analysis": analysis_dict,
                "approvalStatus": "PENDING",
                "approvedBy": None,
                "approvedAt": None,
                "createdBy": "generic_user",
                "createdAt": doc.get("createdAt") if doc.exists else now,
                "updatedAt": now,
                "sessionId": analysis.session_id,
                "workflowName": workflow_name if workflow_name else f"Workflow {workflow_id[:8]}", # Added this line
                "metadata": {
                    "notes": "",
                    "tags": [],
                    "version": 1,
                },
                "orgChart": None,
                "agentRegistry": None,
                "toolRegistry": None,
            }

            doc_ref.set(document_data, merge=True)

        except SerializationError as e:
            raise SerializationError(f"Failed to serialize WorkflowAnalysis: {e}")
        except Exception as e:
            raise FirestoreError(f"Failed to save workflow analysis: {e}")

    def get_workflow_analysis(self, workflow_id: str) -> Optional[WorkflowAnalysis]:
        """
        Retrieve workflow analysis from Firestore.

        Args:
            workflow_id: Unique workflow identifier

        Returns:
            WorkflowAnalysis object or None if not found

        Raises:
            FirestoreError: If Firestore operation fails
            SerializationError: If deserialization fails
        """
        try:
            doc = self.db.collection(self.collection_name).document(workflow_id).get()

            if not doc.exists:
                return None

            analysis_data = doc.get("analysis")
            if not analysis_data:
                return None

            # Deserialize to WorkflowAnalysis
            return WorkflowAnalysis(**analysis_data)

        except Exception as e:
            raise FirestoreError(f"Failed to retrieve workflow analysis: {e}")

    def get_approval_status(self, workflow_id: str) -> Optional[str]:
        """
        Get approval status of a workflow.

        Args:
            workflow_id: Unique workflow identifier

        Returns:
            "PENDING" | "APPROVED" | "REJECTED" | None if not found

        Raises:
            FirestoreError: If Firestore operation fails
        """
        try:
            doc = self.db.collection(self.collection_name).document(workflow_id).get(
                field_paths=["approvalStatus"]
            )

            if not doc.exists:
                return None

            return doc.get("approvalStatus")

        except Exception as e:
            raise FirestoreError(f"Failed to retrieve approval status: {e}")

    def approve_workflow(self, workflow_id: str, approved_by: str) -> Dict[str, Any]:
        """
        Approve a workflow and trigger org design synthesis.

        Args:
            workflow_id: Unique workflow identifier
            approved_by: User identifier approving the workflow

        Returns:
            Updated workflow document

        Raises:
            WorkflowNotFoundError: If workflow doesn't exist
            InvalidApprovalStateError: If workflow is not in PENDING state
            FirestoreError: If Firestore operation fails
        """
        try:
            doc_ref = self.db.collection(self.collection_name).document(workflow_id)
            doc = doc_ref.get()

            if not doc.exists:
                raise WorkflowNotFoundError(f"Workflow {workflow_id} not found")

            current_status = doc.get("approvalStatus")
            if current_status != "PENDING":
                raise InvalidApprovalStateError(
                    f"Workflow {workflow_id} is not in PENDING state. "
                    f"Current status: {current_status}"
                )

            now = datetime.utcnow().isoformat() + "Z"

            # Update approval status in Firestore
            doc_ref.update({
                "approvalStatus": "APPROVED",
                "approvedBy": approved_by,
                "approvedAt": now,
                "updatedAt": now,
            })

            # Auto-trigger org design synthesis and capture results
            org_chart, agent_registry, tool_registry = self._trigger_org_design_synthesis(workflow_id)

            # Construct and return the updated document data directly
            # This avoids a race condition by not re-fetching from Firestore immediately
            return {
                "workflow_id": workflow_id,
                "approvalStatus": "APPROVED",
                "approvedBy": approved_by,
                "approvedAt": now,
                "updatedAt": now,
                "orgChart": org_chart,
                "agentRegistry": agent_registry,
                "toolRegistry": tool_registry,
                "workflowName": doc.get("workflowName"),
            }

        except (WorkflowNotFoundError, InvalidApprovalStateError):
            raise
        except Exception as e:
            raise FirestoreError(f"Failed to approve workflow: {e}")

    def _model_to_dict(self, model_obj: Any) -> Optional[Dict[str, Any]]:
        """Convert Pydantic models or dict-like objects into serializable dicts."""
        if model_obj is None:
            return None

        if hasattr(model_obj, "model_dump"):
            return model_obj.model_dump()

        if isinstance(model_obj, dict):
            return model_obj

        raise SerializationError(
            f"Unsupported type for serialization: {type(model_obj).__name__}"
        )

    def save_org_chart(
        self,
        workflow_id: str,
        org_chart: Any,
        agent_registry: Any,
        tool_registry: Any,
    ) -> None:
        """
        Save org chart and registries to Firestore.

        Args:
            workflow_id: Unique workflow identifier
            org_chart: AgentOrgChart Pydantic model
            agent_registry: Agent registry dictionary
            tool_registry: Tool registry dictionary

        Raises:
            WorkflowNotFoundError: If workflow document doesn't exist
            SerializationError: If serialization fails
            FirestoreError: If Firestore operation fails
        """
        try:
            doc_ref = self.db.collection(self.collection_name).document(workflow_id)
            doc = doc_ref.get()

            if not doc.exists:
                raise WorkflowNotFoundError(f"Workflow {workflow_id} not found")

            # Serialize payloads
            org_chart_dict = self._model_to_dict(org_chart)
            agent_registry_dict = self._model_to_dict(agent_registry)
            tool_registry_dict = self._model_to_dict(tool_registry)

            now = datetime.utcnow().isoformat() + "Z"

            # Update with org chart and registries
            doc_ref.update({
                "orgChart": org_chart_dict,
                "agentRegistry": agent_registry_dict,
                "toolRegistry": tool_registry_dict,
                "updatedAt": now,
            })

        except WorkflowNotFoundError:
            raise
        except SerializationError as e:
            raise SerializationError(f"Failed to serialize org chart: {e}")
        except Exception as e:
            raise FirestoreError(f"Failed to save org chart: {e}")

    def get_org_chart(self, workflow_id: str) -> Optional[AgentOrgChart]:
        """
        Retrieve org chart from Firestore.

        Args:
            workflow_id: Unique workflow identifier

        Returns:
            AgentOrgChart object or None if not found or null

        Raises:
            FirestoreError: If Firestore operation fails
        """
        try:
            doc = self.db.collection(self.collection_name).document(workflow_id).get()

            if not doc.exists:
                return None

            org_chart_data = doc.get("orgChart")
            if not org_chart_data:
                return None

            # Deserialize to AgentOrgChart
            return AgentOrgChart(**org_chart_data)

        except Exception as e:
            raise FirestoreError(f"Failed to retrieve org chart: {e}")

    def list_workflows(
        self,
        approval_status: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        List workflows with optional filtering.

        Args:
            approval_status: Filter by approval status (PENDING|APPROVED|REJECTED)
            limit: Maximum number of results to return

        Returns:
            List of workflow metadata dictionaries

        Raises:
            FirestoreError: If Firestore operation fails
        """
        try:
            query = self.db.collection(self.collection_name)

            # Apply status filter if provided
            if approval_status:
                query = query.where("approvalStatus", "==", approval_status)

            # Order by creation date (newest first)
            query = query.order_by("createdAt", direction="DESCENDING")

            # Limit results
            query = query.limit(limit)

            # Execute query
            docs = query.stream()

            results = []
            for doc in docs:
                data = doc.to_dict()
                results.append({
                    "workflow_id": doc.id,
                    "workflowName": data.get("workflowName"), # Added this line
                    "approvalStatus": data.get("approvalStatus"),
                    "createdAt": data.get("createdAt"),
                    "updatedAt": data.get("updatedAt"),
                    "createdBy": data.get("createdBy"),
                })

            return results

        except Exception as e:
            raise FirestoreError(f"Failed to list workflows: {e}")

    def get_workflow_full(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve complete workflow document.

        Args:
            workflow_id: Unique workflow identifier

        Returns:
            Complete workflow document or None if not found

        Raises:
            FirestoreError: If Firestore operation fails
        """
        try:
            doc = self.db.collection(self.collection_name).document(workflow_id).get()

            if not doc.exists:
                return None

            return doc.to_dict()

        except Exception as e:
            raise FirestoreError(f"Failed to retrieve workflow: {e}")

    def update_workflow_name(self, workflow_id: str, workflow_name: str) -> Dict[str, Any]:
        """Update the user-friendly workflow name."""
        sanitized_name = (workflow_name or "").strip()
        if not sanitized_name:
            raise ValueError("workflow_name must be a non-empty string")

        try:
            doc_ref = self.db.collection(self.collection_name).document(workflow_id)
            doc = doc_ref.get()

            if not doc.exists:
                raise WorkflowNotFoundError(f"Workflow {workflow_id} not found")

            now = datetime.utcnow().isoformat() + "Z"
            doc_ref.update({
                "workflowName": sanitized_name,
                "updatedAt": now,
            })

            updated_doc = doc_ref.get()
            return updated_doc.to_dict()

        except WorkflowNotFoundError:
            raise
        except ValueError:
            raise
        except Exception as e:
            raise FirestoreError(f"Failed to update workflow name: {e}")

    def _trigger_org_design_synthesis(self, workflow_id: str) -> Tuple[AgentOrgChart, Dict, Dict]:
        """
        Trigger org design synthesis after approval.
        ...
        Returns:
            Tuple[AgentOrgChart, Dict, Dict]: The generated org_chart, agent_registry, and tool_registry.
            Returns (None, None, None) if analysis cannot be retrieved or synthesis fails.
        """
        try:
            # Import here to avoid circular imports
            from agent.org_design.service import run_org_design_for_analysis

            # Retrieve the approved workflow analysis
            analysis = self.get_workflow_analysis(workflow_id)
            if not analysis:
                print(f"Warning: Could not retrieve analysis for workflow {workflow_id}")
                return None, None, None # Return Nones on failure

            # Run org design synthesis
            org_chart, agent_registry, tool_registry = run_org_design_for_analysis(
                analysis=analysis,
            )

            org_chart_dict = self._model_to_dict(org_chart)
            agent_registry_dict = self._model_to_dict(agent_registry)
            tool_registry_dict = self._model_to_dict(tool_registry)

            # Save org chart via repository
            self.save_org_chart(
                workflow_id=workflow_id,
                org_chart=org_chart_dict,
                agent_registry=agent_registry_dict,
                tool_registry=tool_registry_dict,
            )

            print(f"✓ Org design synthesis completed and saved for workflow {workflow_id}")
            return org_chart_dict, agent_registry_dict, tool_registry_dict

        except Exception as e:
            # Log error but don't block approval
            print(f"Warning: Org design synthesis failed for workflow {workflow_id}: {e}")
            return None, None, None # Return Nones on failure
