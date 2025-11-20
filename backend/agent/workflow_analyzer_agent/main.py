"""Entry point for workflow analyzer - demonstrates usage and testing."""
import asyncio
import json
from .orchestrator import WorkflowAnalyzerOrchestrator


async def main():
    """
    Main entry point for workflow analysis.

    Example workflow demonstrating all agent types:
    - Data processing steps (automatable)
    - Human review steps (HUMAN agent)
    - Risk and compliance considerations
    """
    workflow_text = """
    Step 1: Receive customer email from inbox
    Step 2: Extract key information and parse structure
    Step 3: Categorize request into predefined categories
    Step 4: Query knowledge base for relevant articles
    Step 5: Generate response draft using AI
    Step 6: Human review and approval of response
    Step 7: Send response email to customer
    Step 8: Log interaction in database
    """

    print("=" * 70)
    print("WORKFLOW ANALYZER - ORCHESTRATOR TEST")
    print("=" * 70)
    print(f"\nAnalyzing workflow:\n{workflow_text}\n")

    try:
        # Initialize orchestrator
        print("[INIT] Initializing WorkflowAnalyzerOrchestrator...")
        orchestrator = WorkflowAnalyzerOrchestrator()
        print("[INIT] Orchestrator initialized successfully\n")

        # Run analysis
        print("[RUNNING] Starting workflow analysis...")
        result = await orchestrator.analyze_workflow(workflow_text)

        # Display results
        print("\n" + "=" * 70)
        print("ANALYSIS RESULTS")
        print("=" * 70)

        print(f"\nWorkflow ID: {result.workflow_id}")
        print(f"Session ID: {result.session_id}")
        print(f"Timestamp: {result.analysis_timestamp}")
        print(f"Analysis Duration: {result.analysis_duration_ms:.2f}ms")

        # Summary statistics
        print(f"\n--- SUMMARY ---")
        print(f"Total Steps: {result.summary.total_steps}")
        print(f"Automatable Steps: {result.summary.automatable_count}")
        print(f"Agent-Required Steps: {result.summary.agent_required_count}")
        print(f"Human-Required Steps: {result.summary.human_required_count}")
        print(f"Automation Potential: {result.summary.automation_potential * 100:.1f}%")
        print(f"High-Risk Steps: {result.summary.high_risk_steps}")
        print(f"Critical-Risk Steps: {result.summary.critical_risk_steps}")

        # Step-by-step breakdown
        print(f"\n--- STEPS BREAKDOWN ---")
        for i, step in enumerate(result.steps, 1):
            print(f"\n[Step {i}] {step.id}: {step.description}")
            print(f"  - Agent Type: {step.agent_type}")
            print(f"  - Risk Level: {step.risk_level}")
            print(f"  - Automation Feasibility: {step.automation_feasibility:.1%}")
            print(f"  - Determinism Score: {step.determinism_score:.1%}")
            if step.available_api:
                print(f"  - Available API: {step.available_api}")
            if step.suggested_tools:
                print(f"  - Suggested Tools: {', '.join(step.suggested_tools)}")
            if step.requires_human_review:
                print(f"  - Human Review Required: YES")

        # Key insights
        print(f"\n--- KEY INSIGHTS ---")
        for i, insight in enumerate(result.key_insights, 1):
            print(f"\n[Insight {i}] {insight.title}")
            print(f"  - Priority: {insight.priority}")
            print(f"  - Description: {insight.description}")
            print(f"  - Affected Steps: {', '.join(insight.affected_steps)}")

        # Recommendations
        print(f"\n--- RECOMMENDATIONS ---")
        for i, rec in enumerate(result.recommendations, 1):
            print(f"{i}. {rec}")

        # Metrics
        print(f"\n--- METRICS ---")
        metrics = orchestrator.get_analysis_metrics()
        print(f"Total Analyses: {metrics['analyses_total']}")
        print(f"Agent 1 Latency: {metrics['agent_1_parser_latency']}")
        print(f"Agent 2 Latency: {metrics['agent_2_risk_latency']}")
        print(f"Agent 3 Latency: {metrics['agent_3_automation_latency']}")

        # Full JSON output
        print(f"\n--- FULL JSON OUTPUT ---")
        print(json.dumps(result.dict(), indent=2, default=str))

        print("\n" + "=" * 70)
        print("ANALYSIS COMPLETED SUCCESSFULLY")
        print("=" * 70)

    except Exception as e:
        print(f"\n[ERROR] Analysis failed: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
