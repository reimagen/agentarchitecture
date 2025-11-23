"""FastAPI application for AgentArchitecture Workflow API."""
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Add backend to path to allow relative imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.firebase_client import FirebaseClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI app.

    Handles startup (initialization) and shutdown (cleanup) events.
    """
    # Startup: Initialize Firebase
    try:
        # Construct an absolute path to the default credentials file for robustness
        backend_dir = Path(__file__).parent.parent.resolve()
        default_creds_path = backend_dir / "firebase-service-account.json"

        firebase_creds_path = os.getenv(
            "FIREBASE_CREDENTIALS_PATH", default_creds_path
        )
        FirebaseClient.initialize(firebase_creds_path)
        print("✓ Firebase initialized on startup")
    except Exception as e:
        print(f"⚠ Failed to initialize Firebase: {e}")
        print("  Continuing without Firebase persistence")

    yield

    # Shutdown: Cleanup (if needed)
    print("✓ Application shutdown")


# Create FastAPI app
app = FastAPI(
    title="AgentArchitecture API",
    description="Workflow analysis and agent org design",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers after app creation to avoid circular imports
from api import workflows, approval

# Include routers
app.include_router(workflows.router)
app.include_router(approval.router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "AgentArchitecture API"}


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "AgentArchitecture Workflow API",
        "version": "1.0.0",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
