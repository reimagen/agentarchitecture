"""Session manager for creating and retrieving analysis sessions."""
from typing import Dict, Optional
from .session_state import SessionState


class SessionManager:
    """
    Manages the lifecycle of workflow analysis sessions.

    This class handles:
    - Creating new sessions with unique identifiers
    - Retrieving existing sessions
    - In-memory session storage (can be extended with persistence layer)
    """

    def __init__(self):
        """Initialize session manager with empty session store."""
        self._sessions: Dict[str, SessionState] = {}

    def create_session(self) -> SessionState:
        """
        Create a new analysis session.

        Returns:
            SessionState: A new session with generated UUIDs and timestamps
        """
        session = SessionState()
        self._sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[SessionState]:
        """
        Retrieve an existing session by ID.

        Args:
            session_id: The unique session identifier

        Returns:
            SessionState if found, None otherwise
        """
        return self._sessions.get(session_id)

    def update_session(self, session_id: str, session: SessionState) -> bool:
        """
        Update an existing session.

        Args:
            session_id: The session identifier
            session: The updated SessionState object

        Returns:
            True if session was updated, False if not found
        """
        if session_id in self._sessions:
            self._sessions[session_id] = session
            return True
        return False

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: The session identifier

        Returns:
            True if session was deleted, False if not found
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def list_sessions(self) -> list[str]:
        """
        List all active session IDs.

        Returns:
            List of session identifiers
        """
        return list(self._sessions.keys())

    def clear_all_sessions(self) -> None:
        """Clear all sessions from memory (useful for testing)."""
        self._sessions.clear()
