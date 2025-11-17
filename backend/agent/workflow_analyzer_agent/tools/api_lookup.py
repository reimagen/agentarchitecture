"""API Lookup Tool - Check if an API exists for automating a step."""
from typing import Dict, Any, Optional
import logging

# Configure logger
logger = logging.getLogger(__name__)


# Mock API Database
API_DATABASE = {
    "email": {
        "api_name": "Gmail API",
        "determinism": 1.0,
        "description": "Send and manage emails"
    },
    "send email": {
        "api_name": "Gmail API",
        "determinism": 1.0,
        "description": "Send and manage emails"
    },
    "draft email": {
        "api_name": "Gmail API",
        "determinism": 1.0,
        "description": "Send and manage emails"
    },
    "database": {
        "api_name": "SQL API",
        "determinism": 1.0,
        "description": "Query and manage relational databases"
    },
    "read file": {
        "api_name": "File System API",
        "determinism": 1.0,
        "description": "Read and write files"
    },
    "write file": {
        "api_name": "File System API",
        "determinism": 1.0,
        "description": "Read and write files"
    },
    "fetch": {
        "api_name": "HTTP API",
        "determinism": 0.9,
        "description": "Make HTTP requests"
    },
    "http": {
        "api_name": "HTTP API",
        "determinism": 0.9,
        "description": "Make HTTP requests"
    },
    "request": {
        "api_name": "HTTP API",
        "determinism": 0.9,
        "description": "Make HTTP requests"
    },
}

# Keywords that indicate no API is available
# These should be checked BEFORE general API keywords
NO_API_KEYWORDS = {
    "human": 0.1,
    "manual": 0.1,
    "review": 0.2,
    "approve": 0.3,
    "validate": 0.4,
    "check": 0.5,
}


def lookup_api_docs(step_description: str, trace_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Check if an API exists for automating a given step.

    This tool searches a mock API database to determine if there's an existing API
    that can automate the given step description.

    Args:
        step_description: Description of the workflow step to automate
        trace_id: Optional trace ID for distributed logging

    Returns:
        Dictionary with structure:
        {
            "api_exists": bool,
            "api_name": Optional[str],
            "determinism": float (0.0-1.0),
            "notes": str,
            "lookup_status": str
        }

    Examples:
        >>> lookup_api_docs("send email to customer")
        {'api_exists': True, 'api_name': 'Gmail API', 'determinism': 1.0, ...}

        >>> lookup_api_docs("review and approve document")
        {'api_exists': False, 'api_name': None, 'determinism': 0.3, ...}
    """
    # Validate input
    if not step_description or not isinstance(step_description, str):
        logger.debug(
            "Invalid step description provided",
            extra={"trace_id": trace_id, "input": step_description}
        )
        return {
            "api_exists": False,
            "api_name": None,
            "determinism": 0.0,
            "notes": "Invalid step description provided",
            "lookup_status": "error"
        }

    # Normalize input for matching
    normalized_desc = step_description.lower().strip()

    # Log the lookup
    logger.debug(
        "API lookup initiated",
        extra={
            "trace_id": trace_id,
            "step_description": step_description
        }
    )

    # Check for no-API keywords FIRST (higher priority)
    for keyword, determinism in NO_API_KEYWORDS.items():
        if keyword in normalized_desc:
            logger.debug(
                "No API available for step type",
                extra={
                    "trace_id": trace_id,
                    "keyword": keyword,
                    "determinism": determinism
                }
            )
            return {
                "api_exists": False,
                "api_name": None,
                "determinism": determinism,
                "notes": f"Step requires {keyword} which typically cannot be fully automated",
                "lookup_status": "no_api_available"
            }

    # Try exact keyword matches after checking no-API keywords
    for keyword, api_info in API_DATABASE.items():
        if keyword in normalized_desc:
            logger.debug(
                "API found via keyword match",
                extra={
                    "trace_id": trace_id,
                    "keyword": keyword,
                    "api_name": api_info["api_name"]
                }
            )
            return {
                "api_exists": True,
                "api_name": api_info["api_name"],
                "determinism": api_info["determinism"],
                "notes": api_info["description"],
                "lookup_status": "found"
            }

    # No match found
    logger.debug(
        "No specific API found for step",
        extra={
            "trace_id": trace_id,
            "step_description": step_description
        }
    )
    return {
        "api_exists": False,
        "api_name": None,
        "determinism": 0.5,
        "notes": "No specific API found. May require custom integration or manual review.",
        "lookup_status": "no_match"
    }
