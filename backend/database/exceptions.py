"""Custom exception classes for database and workflow operations."""


class WorkflowNotFoundError(Exception):
    """Raised when a workflow document is not found in Firestore."""

    pass


class InvalidApprovalStateError(Exception):
    """Raised when attempting to approve a workflow in an invalid state."""

    pass


class ApprovalRequiredException(Exception):
    """Raised when an operation requires approval before proceeding."""

    pass


class FirestoreError(Exception):
    """Raised when a low-level Firestore operation fails."""

    pass


class SerializationError(Exception):
    """Raised when Pydantic model serialization/deserialization fails."""

    pass
