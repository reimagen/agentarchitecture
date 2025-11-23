# Person A - Calvin's ADK Agent Development Plan

## Role: ADK Workflow Analyzer Agent Developer

**Goal:** Build a single, demoable ADK agent that analyzes workflows and outputs JSON recommendations for automation using Google ADK agent types.

**Timeline:** 2-3 days (10-16 hours)

**Demo Priority:** Get something working fast that shows workflow analysis → JSON output with agent type recommendations

---

## Phase 1: Setup & Foundation (Day 1, 4-6 hours)

### 1.1 Google Cloud + ADK Setup (1 hour)
- [ ] Create Google Cloud project
- [ ] Enable Vertex AI API
- [ ] Setup authentication (service account or OAuth)
- [ ] Install ADK: `pip install google-adk --break-system-packages`
- [ ] Verify installation with `python -c "from google import genai; print('OK')"`

**Deliverable:** Working ADK environment

---

### 1.2 Create Project Structure (30 min)
```
agentic_architect_mvp/
├── backend/
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── workflow_analyzer.py      # Main ADK agent
│   │   └── prompts.py                 # System + user prompts
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── workflow_schema.py         # Pydantic models
│   ├── tests/
│   │   └── sample_workflows/
│   │       └── customer_support.txt
│   ├── main.py                        # CLI entry point
│   ├── requirements.txt
│   └── README.md
```

**Deliverable:** Directory structure ready

---

### 1.3 Build the ADK Workflow Analyzer Agent (2-3 hours)

**Task:** Create `backend/agent/workflow_analyzer.py` with:
- WorkflowAnalyzer class that uses `gemini-2.0-flash-exp` model
- System prompt for workflow analysis (see MVP plan)
- `analyze_workflow(workflow_text: str) -> dict` method
- Forces JSON output via `response_mime_type="application/json"`
- Uses low temperature (0.1) for consistent output

**Key Code Pattern:**
```python
from google import genai
import json

class WorkflowAnalyzer:
    def __init__(self):
        self.client = genai.Client()
        self.model = "gemini-2.0-flash-exp"

    def analyze_workflow(self, workflow_text: str) -> dict:
        response = self.client.models.generate_content(
            model=self.model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.1,
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)
```

**Deliverable:** Working ADK agent that returns JSON

---

### 1.4 Create Pydantic Schema (1 hour)

**Task:** Build `backend/schemas/workflow_schema.py` with Pydantic models for:
- WorkflowStep (step_id, description, inputs, outputs, dependencies, etc.)
- AutomationSummary (automatable_count, agent_required_count, human_required_count)
- WorkflowAnalysis (complete root model matching MVP JSON schema)

**Why:** Type safety + validation for agent output

**Deliverable:** Validated Pydantic schema

---

## Phase 2: Integration & Testing (Day 2, 4-6 hours)

### 2.1 Create CLI Entry Point (1 hour)

**Task:** Build `backend/main.py` with:
- `argparse` for CLI: `python main.py analyze --input workflow.txt --output analysis.json`
- File reading (simple .txt/.md support first)
- Error handling for file not found, JSON parsing errors
- Output to JSON file

```bash
python main.py analyze --input customer_support.txt --output analysis.json
```

**Deliverable:** Working CLI that accepts workflow file and outputs JSON

---

### 2.2 Test with Sample Workflows (2-3 hours)

**Task:** Create 3-5 test workflows in `backend/tests/sample_workflows/`:
1. `customer_support.txt` - Email processing (from MVP plan)
2. `invoice_processing.md` - Document handling
3. `simple_workflow.txt` - Very basic (2-3 steps)

**For Each Test:**
- Run agent on workflow
- Validate JSON schema compliance (use Pydantic validation)
- Check if recommendations are sensible
- Document any issues

**Deliverable:** 3-5 tested workflows with validated outputs

---

### 2.3 Iterate on Agent Prompt (1-2 hours)

**Based on test results:**
- If agent output is too verbose → tighten system prompt
- If JSON format is wrong → add JSON schema example to prompt
- If agent type recommendations are off → refine scoring guidelines
- If determinism scores are illogical → add more scoring examples

**Goal:** Agent should produce clean, valid JSON that correctly classifies workflow steps 80%+ of the time

**Deliverable:** Refined agent prompt with better outputs

---

## Phase 3: Polish & Demo (Day 3, 2-4 hours)

### 3.1 Add Logging & Error Handling (30 min)

**Task:**
- Add logging to `backend/main.py` (show what's happening)
- Graceful error handling (malformed workflows, API errors)
- Validation errors from Pydantic should be user-friendly

**Deliverable:** Robust agent that doesn't crash

---

### 3.2 Test with 5-10 Diverse Workflows (1-2 hours)

**Create demo workflows:**
1. Very simple (2 steps)
2. Medium complexity (5-7 steps)
3. Complex with branching (10+ steps)
4. Edge case (circular dependencies, ambiguous steps)
5. Real-world example (actual capstone-adjacent workflow)

**For Each:**
- Run analyzer
- Validate JSON
- Note quality of recommendations

**Deliverable:** Confidence that agent works across diverse inputs

---

### 3.3 Create README & Documentation (30 min)

**Document:**
- How to install dependencies
- How to run the CLI
- Example input/output
- JSON schema explained (what each field means)
- Known limitations
- Future improvements

**Deliverable:** Demo-ready documentation

---

### 3.4 Prepare Capstone Demo (30 min)

**Create a demo scenario:**
- Select 1 compelling workflow (maybe your actual capstone workflow?)
- Run analyzer
- Show JSON output in terminal
- Explain 2-3 key recommendations
- Show agent type mappings visually

**Talking Points:**
- "Single agent analyzes workflows in <30 seconds"
- "Maps workflow steps to appropriate ADK agent types"
- "Identifies where human oversight is required"
- "JSON output can feed into downstream systems"

**Deliverable:** 5-minute demo that's compelling and repeatable

---

## Success Criteria

### Functional
- ✅ ADK agent starts and runs without crashing
- ✅ Accepts workflow text input
- ✅ Outputs valid JSON matching schema
- ✅ JSON validates with Pydantic
- ✅ 3-5 test workflows produce sensible recommendations

### Demonstrable
- ✅ Can run `python main.py analyze --input workflow.txt --output result.json`
- ✅ Output JSON is readable and shows clear automation recommendations
- ✅ Agent type mapping (adk_base, agentic_rag, TOOL, HUMAN) is visible
- ✅ HITL (Human-In-The-Loop) requirements are flagged where appropriate

### Nice-to-Have
- ✅ Determinism scores follow guidelines (APIs = 1.0, creative = 0.0-0.3)
- ✅ Risk/compliance flags are present and relevant
- ✅ README is clear and includes usage examples

---

## Quick Wins for Demo

**Day 1 by Evening:**
- Basic agent works and returns JSON
- Single test workflow produces output

**Day 2 by Noon:**
- 3 test workflows validated
- JSON schema conforms to Pydantic

**Day 2 by Evening:**
- Agent prompt refined, 80% confidence in outputs
- 5 diverse workflows tested

**Day 3 by Noon:**
- Final demo scenario ready
- README written
- 5-minute demo scripted

---

## Potential Blockers & Solutions

| Blocker | Solution |
|---------|----------|
| Google Cloud auth issues | Use `gcloud auth application-default login` |
| ADK installation fails | Try `pip install --upgrade google-adk` |
| JSON output malformed | Add JSON schema example to system prompt |
| Agent type recommendations wrong | Review scoring guidelines in prompt, iterate |
| Pydantic validation fails | Check agent output format, add strict mode |
| Demo file doesn't exist | Create a sample workflow file for demo |

---

## Notes

- **Focus:** Get something demoable ASAP, perfection can wait
- **Philosophy:** Single agent > multiple agents (less complexity)
- **MVP Mindset:** 80/20 rule - spend 20% effort to get 80% of value
- **Capstone Advantage:** This is a great technical demonstrator of understanding agent architecture

---

## Next Immediate Steps

1. **Right now:** Setup Google Cloud project + ADK installation
2. **In 1 hour:** Verify ADK works, create project structure
3. **In 3 hours:** First working agent (even if basic)
4. **By end of Day 1:** Agent produces valid JSON on test workflow
5. **By end of Day 2:** Ready for demo
6. **Day 3:** Polish and present

**You've got this. The key is shipping something demoable fast, not perfection.**
