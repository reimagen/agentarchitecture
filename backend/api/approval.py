"""Workflow approval REST API endpoints."""
import os
import sys
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from backend/.env
env_file = Path(__file__).parent.parent / ".env"
load_dotenv(env_file)

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.exceptions import (
    WorkflowNotFoundError,
    InvalidApprovalStateError,
    FirestoreError,
)
from database.firebase_client import FirebaseClient
from database.workflow_repository import WorkflowRepository


class ApprovalRequest(BaseModel):
    """Request body for workflow approval."""
    approved_by: str = "generic_user"
    notes: Optional[str] = None

router = APIRouter(prefix="/workflows", tags=["approval"])

# Global repository instance
_repository = None


def get_repository():
    """Get or initialize repository."""
    global _repository
    if _repository is None:
        # Ensure Firebase is initialized
        try:
            FirebaseClient.get_db()
        except RuntimeError:
            # Firebase not initialized yet, initialize it
            firebase_creds_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "./firebase-service-account.json")
            FirebaseClient.initialize(firebase_creds_path)

        _repository = WorkflowRepository()
    return _repository


@router.post("/{workflow_id}/approve", status_code=200)
async def approve_workflow(workflow_id: str, request: ApprovalRequest):
    """
    Approve a workflow and trigger org design synthesis.

    Request body:
    {
        "approved_by": "generic_user",
        "notes": "Analysis looks good"
    }

    Processing flow:
    1. Validate workflow exists and status is PENDING
    2. Update approval status in Firestore
    3. Automatically trigger org design synthesis
    4. Return updated workflow with org chart and registries

    Returns:
    {
        "workflow_id": "wf_a1b2c3d4",
        "approvalStatus": "APPROVED",
        "approvedBy": "generic_user",
        "approvedAt": "2025-11-18T20:30:00.000Z",
        "orgChart": { /* AgentOrgChart JSON */ },
        "agentRegistry": { /* Agent registry dict */ },
        "toolRegistry": { /* Tool registry dict */ },
        "updatedAt": "2025-11-18T20:31:00.000Z"
    }

    HTTP Status Codes:
    - 200 OK: Success (approval + synthesis complete)
    - 400 Bad Request: Invalid approval state (already approved/rejected)
    - 404 Not Found: Workflow not found
    - 500 Server Error: Database or synthesis failure
    """
    try:
        approved_by = request.approved_by
        notes = request.notes or ""

        repository = get_repository()

        # Approve workflow (this triggers org design synthesis internally)
        updated_doc = repository.approve_workflow(workflow_id, approved_by)

        # Add notes to metadata if provided
        if notes:
            updated_doc.get("metadata", {})["notes"] = notes

        return {
            "workflow_id": workflow_id,
            "approvalStatus": updated_doc.get("approvalStatus"),
            "approvedBy": updated_doc.get("approvedBy"),
            "approvedAt": updated_doc.get("approvedAt"),
            "orgChart": updated_doc.get("orgChart"),
            "agentRegistry": updated_doc.get("agentRegistry"),
            "toolRegistry": updated_doc.get("toolRegistry"),
            "updatedAt": updated_doc.get("updatedAt"),
        }

    except WorkflowNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidApprovalStateError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to approve workflow: {str(e)}")


@router.get("/{workflow_id}/approval-status")
async def get_approval_status(workflow_id: str):
    """
    Get the approval status of a workflow.

    Returns:
    {
        "workflow_id": "wf_a1b2c3d4",
        "approvalStatus": "PENDING|APPROVED|REJECTED"
    }

    HTTP Status Codes:
    - 200 OK: Success
    - 404 Not Found: Workflow not found
    """
    try:
        repository = get_repository()
        status = repository.get_approval_status(workflow_id)

        if status is None:
            raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")

        return {
            "workflow_id": workflow_id,
            "approvalStatus": status,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get approval status: {str(e)}")
