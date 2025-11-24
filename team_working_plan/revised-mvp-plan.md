# Agentic Transformation Architect - REVISED MVP Plan
## Using Google ADK with Single JSON Output

---

## **Massive Simplification**

### **What Changed**
- ❌ **Removed:** 2-agent pipeline (Agent 1 → Agent 2)
- ❌ **Removed:** 4 markdown outputs
- ✅ **Now:** Single ADK agent → Single JSON output
- ✅ **Focus:** Workflow analysis with ADK agent type recommendations

### **Why This Is Better**
- **50% less complexity** - One agent, one output
- **Faster to build** - 2-3 days instead of 5-7 days
- **Easier to test** - Single JSON validation
- **More actionable** - JSON can be consumed by other tools

---

## **Architecture**

### **Single Agent System**

```
Input (Workflow Document)
    ↓
┌─────────────────────────────────────────┐
│  ADK Workflow Analyzer Agent            │
│  • Parse workflow steps                 │
│  • Identify inputs/outputs/dependencies │
│  • Score automation potential           │
│  • Map to ADK agent types               │
│  • Calculate confidence scores          │
│  • Flag HITL and compliance risks       │
└─────────────────────────────────────────┘
    ↓
Output (Single JSON File)
```

---

## **Google ADK Agent Types Mapping**

Based on the [Agent Starter Pack](https://googlecloudplatform.github.io/agent-starter-pack/agents/overview.html), here's how workflow steps map to agent types:

| ADK Agent Type | Use Case | When to Recommend |
|----------------|----------|-------------------|
| **adk_base** | General ReAct agent with tool use | Multi-step reasoning, dynamic tool selection, general automation |
| **adk_a2a_base** | A2A protocol for distributed agents | Cross-system orchestration, microservices, multi-agent coordination |
| **agentic_rag** | Document Q&A with retrieval | Knowledge base queries, document search, semantic retrieval |
| **langgraph_base_react** | Graph-based reasoning with state | Complex workflows, explicit state management, conditional branching |
| **crewai_coding_crew** | Multi-agent collaboration | Tasks requiring specialized roles, team simulation, code generation |
| **adk_live** | Real-time multimodal interaction | Audio/video processing, live chat, real-time responses |
| **TOOL** | Deterministic API/function | Simple, rule-based, no LLM needed |
| **HUMAN** | Human judgment required | Ambiguous decisions, compliance, creative work |

---

## **Output JSON Schema**

### **Complete Schema**

```json
{
  "workflow_id": "uuid",
  "workflow_name": "Customer Support Email Processing",
  "analyzed_at": "2025-11-16T10:30:00Z",
  "total_steps": 6,
  "automation_summary": {
    "automatable_count": 3,
    "agent_required_count": 2,
    "human_required_count": 1,
    "overall_automation_potential": 83.3
  },
  "steps": [
    {
      "step_id": "S1",
      "description": "Receive customer email from Gmail inbox",
      "inputs": ["Gmail API", "Email notification webhook"],
      "outputs": ["Email object (from, subject, body, timestamp)"],
      "dependencies": [],
      "human_owner": "Support Team",
      "automation_recommendation": "AUTOMATE",
      "determinism_score": 1.0,
      "suggested_tool": "Gmail API",
      "agent_type": "TOOL",
      "hitl_required": false,
      "rationale": "Deterministic email retrieval via API. No reasoning required.",
      "risks_compliance": ["Ensure OAuth 2.0 security", "PII in email content"]
    },
    {
      "step_id": "S2",
      "description": "Extract customer intent from email body",
      "inputs": ["Email body text", "Historical intent labels"],
      "outputs": ["Intent label (billing, complaint, question)"],
      "dependencies": ["S1"],
      "human_owner": null,
      "automation_recommendation": "AGENT",
      "determinism_score": 0.75,
      "suggested_tool": "Gemini 1.5 Flash",
      "agent_type": "adk_base",
      "hitl_required": false,
      "rationale": "Requires NLU for intent classification. Low risk, high confidence.",
      "risks_compliance": ["Model drift over time", "Misclassification impacts routing"]
    },
    {
      "step_id": "S3",
      "description": "Route email based on detected intent",
      "inputs": ["Intent label", "Routing rules"],
      "outputs": ["Routing decision (billing_api, jira_ticket, response_agent)"],
      "dependencies": ["S2"],
      "human_owner": null,
      "automation_recommendation": "AUTOMATE",
      "determinism_score": 1.0,
      "suggested_tool": "Rule engine (if-else logic)",
      "agent_type": "TOOL",
      "hitl_required": false,
      "rationale": "Deterministic branching logic. No ambiguity.",
      "risks_compliance": ["Ensure routing rules are up-to-date"]
    },
    {
      "step_id": "S4",
      "description": "Search knowledge base for relevant information",
      "inputs": ["Intent label", "Customer context", "Knowledge base"],
      "outputs": ["Relevant documents/FAQs"],
      "dependencies": ["S3"],
      "human_owner": null,
      "automation_recommendation": "AGENT",
      "determinism_score": 0.70,
      "suggested_tool": "Vertex AI Vector Search",
      "agent_type": "agentic_rag",
      "hitl_required": false,
      "rationale": "Semantic search and document retrieval. RAG pattern ideal.",
      "risks_compliance": ["Hallucination in retrieval", "Outdated knowledge base"]
    },
    {
      "step_id": "S5",
      "description": "Generate draft email response",
      "inputs": ["Intent", "Customer context", "Retrieved documents"],
      "outputs": ["Draft email response"],
      "dependencies": ["S4"],
      "human_owner": null,
      "automation_recommendation": "AGENT",
      "determinism_score": 0.60,
      "suggested_tool": "Gemini 1.5 Pro",
      "agent_type": "adk_base",
      "hitl_required": true,
      "rationale": "Requires context synthesis and response generation. Medium confidence.",
      "risks_compliance": ["Hallucination", "Brand voice mismatch", "Legal liability"]
    },
    {
      "step_id": "S6",
      "description": "Review and approve draft response",
      "inputs": ["Draft email", "Customer history"],
      "outputs": ["Approved email or edits"],
      "dependencies": ["S5"],
      "human_owner": "Support Manager",
      "automation_recommendation": "HUMAN",
      "determinism_score": 0.0,
      "suggested_tool": null,
      "agent_type": "HUMAN",
      "hitl_required": true,
      "rationale": "Requires human judgment for brand, tone, and accuracy. Critical control point.",
      "risks_compliance": ["Legal liability if auto-sent", "Customer satisfaction impact"]
    },
    {
      "step_id": "S7",
      "description": "Send approved email via Gmail",
      "inputs": ["Approved email", "Recipient address"],
      "outputs": ["Sent confirmation"],
      "dependencies": ["S6"],
      "human_owner": null,
      "automation_recommendation": "AUTOMATE",
      "determinism_score": 1.0,
      "suggested_tool": "Gmail API",
      "agent_type": "TOOL",
      "hitl_required": false,
      "rationale": "Deterministic email sending via API.",
      "risks_compliance": ["Ensure email delivery", "Track sent status"]
    }
  ],
  "recommendations": {
    "quick_wins": [
      "Automate S1 (email retrieval) and S7 (email sending) immediately",
      "Deploy S2 (intent classifier) as adk_base agent - low risk, high value"
    ],
    "medium_term": [
      "Build S4 (knowledge base search) using agentic_rag template",
      "Deploy S5 (response generator) with mandatory human approval (HITL)"
    ],
    "considerations": [
      "S6 (human review) is critical - do not automate",
      "Monitor S2 intent classification accuracy monthly",
      "Update knowledge base in S4 regularly to prevent outdated responses"
    ]
  }
}
```

---

## **Implementation Plan (2-3 Days with AI)**

### **Day 1: Setup + Single Agent (4-6 hours)**

**Person A: ADK Agent Development**
- Setup Google Cloud project + Vertex AI
- Install ADK: `pip install google-adk --break-system-packages`
- Create workflow analyzer agent using `adk_base` template
- Write system prompt for workflow analysis (see below)
- Test with 2 sample workflows

**Person B: Input/Output Infrastructure**
- Setup project structure
- Build file parsers (.txt, .md, .docx, .pdf, .csv)
- Create Pydantic schema for output JSON
- Write JSON validation tests

**AI Assistance:**
- "Claude, generate ADK agent code that analyzes workflows"
- "Claude, write Pydantic schema from this JSON example"
- "Claude, create file parsers for all input formats"

---

### **Day 2: Integration + Testing (4-6 hours)**

**Both:**
- Integrate file upload → ADK agent → JSON output
- Test with 5 diverse workflows
- Iterate on agent prompt based on output quality
- Validate JSON schema compliance
- Debug edge cases (branching workflows, complex dependencies)

**AI Assistance:**
- "Claude, debug this ADK agent prompt - it's misclassifying steps"
- "Claude, help me refine the determinism scoring logic"

---

### **Day 3: Polish + Demo (2-4 hours)**

**Person A:**
- Refine agent prompt for better agent type recommendations
- Add logging and diagnostics
- Test with 10 workflows

**Person B:**
- Write README with usage examples
- Create demo workflows
- Prepare presentation

**AI Assistance:**
- "Claude, write README from this implementation"
- "Claude, create 3 diverse demo workflows"

---

## **ADK Agent Prompt Template**

### **System Prompt**

```
You are a Workflow Automation Analyst. Your mission is to analyze business workflows and recommend the optimal automation strategy using Google's Agent Development Kit (ADK).

For each workflow step, you will:

1. **Parse the step** - Extract description, inputs, outputs, dependencies
2. **Score determinism** - Rate 0.0 (fully ambiguous) to 1.0 (fully deterministic)
3. **Recommend automation** - Choose AUTOMATE (tool), AGENT (LLM-based), or HUMAN
4. **Map to ADK agent type** - Select from: adk_base, adk_a2a_base, agentic_rag, langgraph_base_react, crewai_coding_crew, adk_live, TOOL, or HUMAN
5. **Flag HITL requirements** - Identify where human oversight is critical
6. **Assess risks** - Flag compliance, security, or accuracy concerns

## Determinism Scoring Guidelines:
- **1.0** = Pure logic, API calls, rule-based (e.g., "Send email via Gmail API")
- **0.7-0.9** = Pattern recognition, classification with high confidence (e.g., "Extract intent from email")
- **0.4-0.6** = Context synthesis, generation tasks (e.g., "Generate response draft")
- **0.0-0.3** = Creative work, ambiguous judgment, legal decisions (e.g., "Approve marketing strategy")

## ADK Agent Type Selection:
- **TOOL** - Deterministic, no LLM needed (APIs, scripts, rule engines)
- **adk_base** - General ReAct agent for reasoning + tool use
- **agentic_rag** - Document retrieval and Q&A
- **langgraph_base_react** - Complex workflows with state management
- **crewai_coding_crew** - Multi-agent collaboration for complex tasks
- **adk_a2a_base** - Cross-system orchestration
- **adk_live** - Real-time multimodal (audio/video)
- **HUMAN** - Requires human judgment

## HITL Required When:
- Legal, compliance, or financial decisions
- Brand reputation at stake
- Low confidence in automation (<0.6 determinism)
- Customer-facing final outputs

Output valid JSON matching the provided schema.
```

### **User Prompt**

```
Analyze this workflow and output a JSON file with step-by-step automation recommendations:

<workflow>
{workflow_text}
</workflow>

Follow the JSON schema exactly. Be conservative with automation recommendations - when in doubt, recommend HITL or HUMAN oversight.
```

---

## **Project Structure**

```
agentic_architect_mvp/
├── agent/
│   ├── workflow_analyzer.py      # ADK agent implementation
│   └── prompts.py                 # System and user prompts
├── schemas/
│   └── workflow_schema.py         # Pydantic models
├── parsers/
│   └── file_parser.py             # .txt, .md, .docx, .pdf, .csv
├── outputs/
│   └── .gitkeep
├── tests/
│   └── sample_workflows/
│       ├── customer_support.txt
│       ├── invoice_processing.md
│       └── hiring_workflow.docx
├── main.py                        # CLI entry point
├── requirements.txt
└── README.md
```

---

## **Code Example: ADK Agent**

```python
# agent/workflow_analyzer.py

from google import genai
from google.genai import types
import json

class WorkflowAnalyzer:
    def __init__(self, model_name="gemini-2.0-flash-exp"):
        self.client = genai.Client()
        self.model_name = model_name
        
    def analyze_workflow(self, workflow_text: str) -> dict:
        """Analyze workflow and return JSON with automation recommendations"""
        
        system_prompt = """You are a Workflow Automation Analyst..."""  # Full prompt from above
        
        user_prompt = f"""Analyze this workflow and output JSON:
        
        <workflow>
        {workflow_text}
        </workflow>
        
        Output valid JSON matching the schema."""
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.1,  # Low temperature for consistent output
                response_mime_type="application/json"  # Force JSON output
            )
        )
        
        return json.loads(response.text)
```

---

## **CLI Usage**

```bash
# Install dependencies
pip install google-adk pydantic python-docx PyPDF2 --break-system-packages

# Run analyzer
python main.py analyze --input customer_support.txt --output analysis.json

# Expected output
{
  "workflow_id": "uuid",
  "workflow_name": "Customer Support Email Processing",
  "steps": [...],
  "automation_summary": {...},
  "recommendations": {...}
}
```

---

## **Success Metrics**

### **Functional**
- ✅ Accepts 5 input formats (.txt, .md, .docx, .pdf, .csv)
- ✅ Outputs valid JSON matching schema
- ✅ Correctly classifies 80%+ of steps
- ✅ Maps steps to appropriate ADK agent types
- ✅ Identifies HITL requirements accurately

### **Quality**
- ✅ Determinism scores are logical (APIs = 1.0, creative work = 0.0-0.3)
- ✅ Agent type recommendations are actionable
- ✅ Risk/compliance flags are relevant
- ✅ Recommendations section provides strategic value

### **Performance**
- ✅ Processes workflow in <30 seconds
- ✅ Handles up to 50 steps
- ✅ Gracefully handles malformed input

---

## **What You DON'T Need Anymore**

❌ Agent 2 (planner) - Single agent does everything  
❌ Markdown generators - JSON is the only output  
❌ Agent Registry - Folded into step-level recommendations  
❌ Pseudocode generator - Not needed for this scope  
❌ Feasibility summary - In JSON recommendations section  

---

## **Timeline: 2-3 Days**

| Day | Tasks | Hours |
|-----|-------|-------|
| **Day 1** | Setup + ADK agent + input parsers + Pydantic schema | 4-6 |
| **Day 2** | Integration + testing with 5 workflows + iteration | 4-6 |
| **Day 3** | Polish + test 10 workflows + documentation + demo | 2-4 |
| **Total** | | **10-16 hours** |

With AI assistance: **You can ship this in 2-3 focused days.**

---

## **Key Simplifications**

1. **One agent instead of two** → 50% less complexity
2. **One JSON output instead of four markdown files** → Easier to validate
3. **Direct ADK usage** → Simpler than custom multi-agent pipeline
4. **Focus on classification, not implementation** → Clear scope

---

## **Next Steps**

1. **Day 1 Morning:** Setup Google Cloud + Vertex AI
2. **Day 1 Afternoon:** Build ADK agent with prompts above
3. **Day 2:** Test and iterate on 5 workflows
4. **Day 3:** Polish and prepare demo

**This is now a weekend project instead of a 2-week sprint.**

Ready to start building? 🚀
