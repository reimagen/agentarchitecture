# Step 2: Custom Tools Implementation

**Estimated Time:** 30 minutes
**Status:** Not Started
**Goal:** Create the two custom tools that agents will call

## Background

These tools are called by the agents to make better decisions:
- **Agent 2** (Risk Assessor) calls `get_compliance_rules()`
- **Agent 3** (Automation Analyzer) calls `lookup_api_docs()`

For this MVP, we'll use mock/simulated data. In production, these would query real databases.

## Tasks

### 2.1 Create API Lookup Tool
**File:** `tools/api_lookup.py`

Create function `lookup_api_docs(step_description: str) -> dict`

Purpose: Check if an API exists for automating a given step

Returns a dict with:
- `api_exists` (bool): Does an API exist?
- `api_name` (str): Name of the API (or None)
- `determinism` (float): 0.0-1.0 how deterministic is this API
- `notes` (str): Additional context

**Implementation:**
- Use keyword matching on `step_description` to look up APIs
- Example database (hardcoded for MVP):
  ```
  "email" → Gmail API (exists, determinism=1.0)
  "database" → SQL API (exists, determinism=1.0)
  "draft email" → Gmail API (exists, determinism=1.0)
  "review" → No API (doesn't exist, determinism=0.2)
  "approve" → No API (doesn't exist, determinism=0.3)
  "read file" → File System API (exists, determinism=1.0)
  "write file" → File System API (exists, determinism=1.0)
  "fetch" → HTTP API (exists, determinism=0.9)
  ```
- If no exact match, return "No specific API found"
- Log the lookup (include trace_id if available)

### 2.2 Create Compliance Rules Tool
**File:** `tools/compliance_checker.py`

Create function `get_compliance_rules(risk_level: str, domain: str) -> dict`

Purpose: Return applicable compliance rules for a given risk level and domain

Returns a dict with:
- `applicable_rules` (list[str]): Which regulations apply
- `requires_audit` (bool): Does this require an audit?
- `hitl_required` (bool): Must a human be in the loop?

**Implementation:**
- Use combination of `risk_level` and `domain` to look up rules
- Example database (hardcoded for MVP):
  ```
  ("CRITICAL", "financial") → ["SOX", "PCI-DSS"], requires_audit=True, hitl_required=True
  ("CRITICAL", "healthcare") → ["HIPAA", "HITECH"], requires_audit=True, hitl_required=True
  ("HIGH", "financial") → ["PCI-DSS"], requires_audit=True, hitl_required=False
  ("HIGH", "healthcare") → ["HIPAA"], requires_audit=False, hitl_required=True
  ("MEDIUM", "general") → [], requires_audit=False, hitl_required=False
  ("LOW", "general") → [], requires_audit=False, hitl_required=False
  ("CRITICAL", "*") → Always requires_audit=True, hitl_required=True
  ```
- If no match, default to: `{"applicable_rules": [], "requires_audit": False, "hitl_required": False}`
- Log the lookup (include trace_id if available)

### 2.3 Add Tool Integrations
**File:** `tools/__init__.py`

Export both tools so they can be imported:
```python
from .api_lookup import lookup_api_docs
from .compliance_checker import get_compliance_rules

__all__ = ["lookup_api_docs", "get_compliance_rules"]
```

## Tool Signature Notes

Both tools should have:
- Clear docstrings explaining what they return
- Type hints (input and output)
- Error handling for invalid inputs (log and return sensible defaults)
- Logging statements for each tool call (at DEBUG level)

## Acceptance Criteria

- [ ] `tools/api_lookup.py` created with `lookup_api_docs()` function
- [ ] `tools/compliance_checker.py` created with `get_compliance_rules()` function
- [ ] Both tools return correct dict structure
- [ ] Both tools handle edge cases (empty strings, invalid risk_level, etc.)
- [ ] Both tools log their calls
- [ ] `tools/__init__.py` exports both functions
- [ ] Can import both functions without errors: `from tools import lookup_api_docs, get_compliance_rules`
- [ ] Manual tests pass for common scenarios:
  - `lookup_api_docs("send email")` → returns Gmail API info
  - `lookup_api_docs("review document")` → returns "No API found"
  - `get_compliance_rules("CRITICAL", "financial")` → returns SOX, PCI-DSS, requires_audit=True
  - `get_compliance_rules("LOW", "general")` → returns empty rules, no audit needed

## Notes

- These are synchronous functions (not async) for now
- MVP uses hardcoded data (no real database lookups)
- Each tool can be tested independently
- Tools are called by agents, so keep responses simple and JSON-serializable

## Next Step

→ Once complete, move to **Step 3: Individual Agents Implementation**
