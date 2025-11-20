#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test script to verify all imports work correctly."""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

print("Testing imports...\n")

try:
    print("1. Testing database imports...")
    from database.firebase_client import FirebaseClient
    print("   [OK] FirebaseClient")

    from database.exceptions import WorkflowNotFoundError
    print("   [OK] Exceptions")

    from database.workflow_repository import WorkflowRepository
    print("   [OK] WorkflowRepository")
except Exception as e:
    print(f"   [FAIL] Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n2. Testing API imports...")
    from api.workflows import router as workflows_router
    print("   [OK] workflows router")

    from api.approval import router as approval_router
    print("   [OK] approval router")
except Exception as e:
    print(f"   [FAIL] Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n3. Testing FastAPI app...")
    from api.app import app
    print("   [OK] FastAPI app")
except Exception as e:
    print(f"   [FAIL] Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[SUCCESS] All imports successful!")
print("\nTo run the API server:")
print("  python -m backend.api.app")
print("  OR")
print("  uvicorn backend.api.app:app --reload --host 0.0.0.0 --port 8000")
