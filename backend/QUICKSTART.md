# Workflow Analyzer Agent - Quick Start Guide

## Installation & Setup

### 1. Install Dependencies

```bash
pip install pydantic google-generativeai
```

### 2. Set Up Gemini API Key

You need a Google Gemini API key. Set it as an environment variable:

**Windows (PowerShell):**
```powershell
$env:GOOGLE_API_KEY = "your-api-key-here"
```

**Windows (Command Prompt):**
```cmd
set GOOGLE_API_KEY=your-api-key-here
```

**Windows (Permanent - via .env file):**
Create a `.env` file in the project root:
```
GOOGLE_API_KEY=your-api-key-here
```

**Linux/Mac:**
```bash
export GOOGLE_API_KEY="your-api-key-here"
```

## Running the Program

### Method 1: Run with Default Sample Workflow (Recommended for First Time)

```bash
cd C:\Users\Calvin\ai-projects\agentarchitecture\backend
python -m backend
```

This will analyze a sample customer support workflow with 8 steps.

### Method 2: Analyze Your Own Workflow (Inline)

```bash
python -m backend --workflow "Step 1: Read file\nStep 2: Process data\nStep 3: Write output"
```

### Method 3: Analyze Workflow from File

Create a file (e.g., `my_workflow.txt`):
```
Step 1: Receive email
Step 2: Extract information
Step 3: Categorize request
Step 4: Query knowledge base
Step 5: Generate response
Step 6: Human review
Step 7: Send email
```

Then run:
```bash
python -m backend --file my_workflow.txt
```

### Method 4: Verbose Output (See All Details)

```bash
python -m backend --verbose
```

This shows detailed breakdown of each step.

### Method 5: JSON Output

```bash
python -m backend --json
```

This outputs the complete analysis as JSON.

### Method 6: Combine Options

```bash
python -m backend --file workflow.txt --verbose --json
```

## Program Output

The program will display:

1. **Workflow Summary**
   - Total steps parsed
   - Automatable steps count
   - Automation potential percentage
   - Risk levels detected

2. **Step-by-Step Analysis** (with `--verbose`)
   - Step ID and description
   - Recommended agent type
   - Risk level
   - Automation feasibility
   - Suggested tools

3. **Key Insights**
   - Automation opportunities
   - Risk and compliance issues
   - Manual review bottlenecks

4. **Recommendations**
   - Actionable suggestions for automation
   - Compliance and risk mitigation

5. **Metrics**
   - Analysis duration
   - Agent latencies
   - Tool call counts

## Example: Simple 3-Step Workflow

```bash
python -m backend --workflow "Step 1: Read file
Step 2: Process data
Step 3: Write output"
```

**Expected Output:**
```
Total Steps: 3
Automatable Steps: 3
Automation Potential: 100.0%

[Step 1] step_1: Read file
  - Agent Type: TOOL
  - Risk Level: LOW
  - Automation Feasibility: 95.0%
  - Available API: File System API

[Step 2] step_2: Process data
  - Agent Type: adk_base
  - Risk Level: MEDIUM
  - Automation Feasibility: 80.0%

[Step 3] step_3: Write output
  - Agent Type: TOOL
  - Risk Level: LOW
  - Automation Feasibility: 95.0%
  - Available API: File System API
```

## Example: Complex Workflow with Human Review

```bash
python -m backend --workflow "Step 1: Receive email
Step 2: Extract info
Step 3: Categorize
Step 4: Check KB
Step 5: Draft response
Step 6: Human review
Step 7: Send email"
```

**Expected Output:**
```
Total Steps: 7
Automatable Steps: 6
Human-Required Steps: 1
Automation Potential: 85.7%

Key Insights:
- Strong Automation Potential: 6/7 steps can be automated
- Manual Review Bottleneck: 1/7 steps requires human review
```

## Troubleshooting

### Error: `ModuleNotFoundError: No module named 'google.generativeai'`

**Solution:**
```bash
pip install google-generativeai
```

### Error: `GOOGLE_API_KEY not set`

**Solution:** Set your Gemini API key:

```bash
# Windows PowerShell
$env:GOOGLE_API_KEY = "your-key"

# Windows Command Prompt
set GOOGLE_API_KEY=your-key

# Linux/Mac
export GOOGLE_API_KEY="your-key"
```

### Error: `Pydantic validation error`

**Solution:** Make sure pydantic is installed:
```bash
pip install pydantic
```

### Error: `API call timeout`

The Gemini API call may take a while. The default timeout is 30 seconds. For complex workflows, this may need to be increased in the `config.py` file.

### Error: `JSON parsing error`

This usually means the Gemini API response wasn't valid JSON. Try again, as this is often a transient issue.

## Project Structure

```
backend/
├── __main__.py                 # Main entry point (YOU ARE HERE)
├── agent/
│   └── workflow_analyzer_agent/
│       ├── orchestrator.py     # Main orchestrator
│       ├── config.py           # Configuration
│       ├── types.py            # Type definitions
│       ├── agents/             # The 3 agents
│       │   ├── agent1_parser.py
│       │   ├── agent2_risk_assessor.py
│       │   └── agent3_automation_analyzer.py
│       ├── tools/              # Custom tools
│       │   ├── api_lookup.py
│       │   └── compliance_checker.py
│       ├── session/            # Session management
│       └── observability/      # Logging, tracing, metrics
├── requirements.txt
└── QUICKSTART.md               # This file
```

## Next Steps

1. Run the program with `python -m backend`
2. Review the analysis results
3. Try different workflows with `--workflow` or `--file`
4. Check metrics with detailed analysis
5. Integrate with your own workflow data

## System Architecture

The Workflow Analyzer uses 3 specialized agents:

**Agent 1: Workflow Parser**
- Parses workflow text into structured steps
- Identifies dependencies between steps
- Extracts inputs and outputs

**Agent 2: Risk Assessor**
- Evaluates risk level for each step
- Identifies compliance requirements
- Flags human-in-the-loop needs

**Agent 3: Automation Analyzer**
- Determines best agent type for each step
- Scores automation feasibility
- Identifies available APIs

The orchestrator runs Agent 1 sequentially, then runs Agents 2 & 3 in parallel, then merges results into comprehensive analysis.

## Performance

- Agent 1 (parsing): ~0.5-2 seconds
- Agent 2 (risk): ~1-3 seconds
- Agent 3 (automation): ~1-3 seconds
- Total (parallel): ~2-5 seconds

## Support

For issues or questions, check:
1. TEST_RESULTS.md - Testing documentation
2. The step files (step1.md through step5.md) - Implementation details
3. Error messages with `--verbose` flag

---

**Status:** Production Ready
**Last Updated:** November 17, 2025
