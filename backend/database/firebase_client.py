"""Firebase initialization and client management module."""
import os
from typing import Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class FirebaseClient:
    """Singleton Firebase client for Firestore database access."""

    _instance: Optional["FirebaseClient"] = None

    def __init__(self):
        """Initialize Firebase client with admin SDK."""
        self.db = None
        self.app = None
        self._initialized = False

    @classmethod
    def initialize(cls, credentials_path: Optional[str] = None) -> "FirebaseClient":
        """
        Initialize Firebase Admin SDK using service account credentials.

        Args:
            credentials_path: Path to service account JSON file.
                            If None, uses FIREBASE_CREDENTIALS_PATH from .env

        Returns:
            FirebaseClient: Singleton instance

        Raises:
            FileNotFoundError: If credentials file not found
            RuntimeError: If Firebase initialization fails
        """
        if cls._instance and cls._instance._initialized:
            return cls._instance

        if cls._instance is None:
            cls._instance = cls()

        # Determine credentials path
        creds_path = credentials_path or os.getenv("FIREBASE_CREDENTIALS_PATH")
        if not creds_path:
            raise RuntimeError(
                "FIREBASE_CREDENTIALS_PATH not provided and not set in environment variables"
            )

        if not os.path.exists(creds_path):
            raise FileNotFoundError(f"Firebase credentials file not found: {creds_path}")

        try:
            import firebase_admin
            from firebase_admin import credentials, firestore

            # Initialize Firebase Admin SDK
            cred = credentials.Certificate(creds_path)
            cls._instance.app = firebase_admin.initialize_app(cred)
            cls._instance.db = firestore.client()
            cls._instance._initialized = True

            print(f"✓ Firebase initialized successfully using credentials: {creds_path}")
            return cls._instance

        except ImportError as e:
            raise RuntimeError(
                f"Firebase Admin SDK not installed. Install with: pip install firebase-admin. Error: {e}"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Firebase: {e}")

    @classmethod
    def get_db(cls):
        """
        Get Firestore client instance.

        Returns:
            firestore.Client: Firestore database client

        Raises:
            RuntimeError: If Firebase not initialized
        """
        if cls._instance is None or not cls._instance._initialized:
            raise RuntimeError(
                "Firebase not initialized. Call FirebaseClient.initialize() first."
            )
        return cls._instance.db

    @classmethod
    def get_instance(cls) -> "FirebaseClient":
        """
        Get singleton instance.

        Returns:
            FirebaseClient: Singleton instance

        Raises:
            RuntimeError: If Firebase not initialized
        """
        if cls._instance is None or not cls._instance._initialized:
            raise RuntimeError(
                "Firebase not initialized. Call FirebaseClient.initialize() first."
            )
        return cls._instance

    @classmethod
    def get_timestamp(cls):
        """
        Get server timestamp for consistent timestamping.

        Returns:
            Timestamp: Firebase server timestamp

        Raises:
            RuntimeError: If Firebase not initialized
        """
        from firebase_admin.firestore import SERVER_TIMESTAMP

        if cls._instance is None or not cls._instance._initialized:
            raise RuntimeError(
                "Firebase not initialized. Call FirebaseClient.initialize() first."
            )
        return SERVER_TIMESTAMP
