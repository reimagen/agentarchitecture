"""Compliance Rules Tool - Return applicable compliance rules for a given risk level and domain."""
from typing import Dict, List, Any, Optional
import logging

# Configure logger
logger = logging.getLogger(__name__)


# Mock Compliance Database
# Structure: (risk_level, domain) -> {applicable_rules, requires_audit, hitl_required}
COMPLIANCE_DATABASE = {
    ("CRITICAL", "financial"): {
        "applicable_rules": ["SOX", "PCI-DSS"],
        "requires_audit": True,
        "hitl_required": True
    },
    ("CRITICAL", "healthcare"): {
        "applicable_rules": ["HIPAA", "HITECH"],
        "requires_audit": True,
        "hitl_required": True
    },
    ("HIGH", "financial"): {
        "applicable_rules": ["PCI-DSS"],
        "requires_audit": True,
        "hitl_required": False
    },
    ("HIGH", "healthcare"): {
        "applicable_rules": ["HIPAA"],
        "requires_audit": False,
        "hitl_required": True
    },
    ("MEDIUM", "general"): {
        "applicable_rules": [],
        "requires_audit": False,
        "hitl_required": False
    },
    ("LOW", "general"): {
        "applicable_rules": [],
        "requires_audit": False,
        "hitl_required": False
    },
}

# Default values for unmatched combinations
DEFAULT_COMPLIANCE = {
    "applicable_rules": [],
    "requires_audit": False,
    "hitl_required": False
}


def get_compliance_rules(
    risk_level: str,
    domain: str,
    trace_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Return applicable compliance rules for a given risk level and domain.

    This tool looks up compliance requirements based on the risk level and domain
    of a workflow step. It helps determine what regulations apply and whether
    human oversight or audits are required.

    Args:
        risk_level: Risk level of the step (LOW, MEDIUM, HIGH, CRITICAL)
        domain: Domain/industry context (financial, healthcare, general, etc.)
        trace_id: Optional trace ID for distributed logging

    Returns:
        Dictionary with structure:
        {
            "applicable_rules": List[str],
            "requires_audit": bool,
            "hitl_required": bool,
            "lookup_status": str,
            "notes": Optional[str]
        }

    Examples:
        >>> get_compliance_rules("CRITICAL", "financial")
        {
            'applicable_rules': ['SOX', 'PCI-DSS'],
            'requires_audit': True,
            'hitl_required': True,
            ...
        }

        >>> get_compliance_rules("LOW", "general")
        {
            'applicable_rules': [],
            'requires_audit': False,
            'hitl_required': False,
            ...
        }
    """
    # Validate inputs
    if not risk_level or not isinstance(risk_level, str):
        logger.debug(
            "Invalid risk level provided",
            extra={"trace_id": trace_id, "risk_level": risk_level}
        )
        return _build_response(
            DEFAULT_COMPLIANCE,
            "error",
            "Invalid risk level provided",
            trace_id
        )

    if not domain or not isinstance(domain, str):
        logger.debug(
            "Invalid domain provided",
            extra={"trace_id": trace_id, "domain": domain}
        )
        return _build_response(
            DEFAULT_COMPLIANCE,
            "error",
            "Invalid domain provided",
            trace_id
        )

    # Normalize inputs
    normalized_risk = risk_level.upper().strip()
    normalized_domain = domain.lower().strip()

    # Log the lookup
    logger.debug(
        "Compliance rule lookup initiated",
        extra={
            "trace_id": trace_id,
            "risk_level": normalized_risk,
            "domain": normalized_domain
        }
    )

    # Check for CRITICAL risk level (always requires audit and HITL)
    if normalized_risk == "CRITICAL":
        result = {
            "applicable_rules": _get_critical_rules(normalized_domain),
            "requires_audit": True,
            "hitl_required": True
        }
        logger.debug(
            "CRITICAL risk level detected - audit and HITL required",
            extra={"trace_id": trace_id, "domain": normalized_domain}
        )
        return _build_response(result, "found", "CRITICAL risk requires audit and human review", trace_id)

    # Try exact match in database
    db_key = (normalized_risk, normalized_domain)
    if db_key in COMPLIANCE_DATABASE:
        result = COMPLIANCE_DATABASE[db_key]
        logger.debug(
            "Compliance rules found",
            extra={
                "trace_id": trace_id,
                "risk_level": normalized_risk,
                "domain": normalized_domain,
                "rules": result["applicable_rules"]
            }
        )
        return _build_response(result, "found", None, trace_id)

    # Try with wildcard domain (risk_level, *)
    wildcard_key = (normalized_risk, "*")
    if wildcard_key in COMPLIANCE_DATABASE:
        result = COMPLIANCE_DATABASE[wildcard_key]
        logger.debug(
            "Compliance rules found via wildcard domain",
            extra={
                "trace_id": trace_id,
                "risk_level": normalized_risk,
                "rules": result["applicable_rules"]
            }
        )
        return _build_response(result, "found", "Using generic rules for this risk level", trace_id)

    # No specific match - return defaults
    logger.debug(
        "No specific compliance rules found - using defaults",
        extra={
            "trace_id": trace_id,
            "risk_level": normalized_risk,
            "domain": normalized_domain
        }
    )
    return _build_response(
        DEFAULT_COMPLIANCE,
        "no_match",
        "No specific rules found for this risk/domain combination",
        trace_id
    )


def _get_critical_rules(domain: str) -> List[str]:
    """
    Get applicable rules for CRITICAL risk level across all domains.

    Args:
        domain: The domain/industry

    Returns:
        List of applicable compliance rules
    """
    rules_map = {
        "financial": ["SOX", "PCI-DSS"],
        "healthcare": ["HIPAA", "HITECH"],
    }
    return rules_map.get(domain, ["General Compliance Review Required"])


def _build_response(
    compliance_data: Dict[str, Any],
    lookup_status: str,
    notes: Optional[str],
    trace_id: Optional[str]
) -> Dict[str, Any]:
    """
    Build a standardized compliance response.

    Args:
        compliance_data: Base compliance data
        lookup_status: Status of the lookup (found, no_match, error)
        notes: Optional additional notes
        trace_id: Optional trace ID

    Returns:
        Complete compliance response dictionary
    """
    response = {
        "applicable_rules": compliance_data.get("applicable_rules", []),
        "requires_audit": compliance_data.get("requires_audit", False),
        "hitl_required": compliance_data.get("hitl_required", False),
        "lookup_status": lookup_status,
    }

    if notes:
        response["notes"] = notes

    if trace_id:
        response["trace_id"] = trace_id

    return response
