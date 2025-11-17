"""
Main entry point for Workflow Analyzer Agent

Run with: python -m backend
or: python -m backend --help
"""
import asyncio
import argparse
import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from agent.workflow_analyzer_agent.orchestrator import WorkflowAnalyzerOrchestrator


async def run_analysis(workflow_text: str, verbose: bool = False):
    """Run workflow analysis with the orchestrator."""
    try:
        # Initialize orchestrator
        print("\n" + "=" * 80)
        print("WORKFLOW ANALYZER AGENT")
        print("=" * 80)
        print("\nInitializing orchestrator...")
        orchestrator = WorkflowAnalyzerOrchestrator()
        print("Orchestrator initialized successfully!\n")

        # Display workflow
        print("Input Workflow:")
        print("-" * 80)
        print(workflow_text)
        print("-" * 80)

        # Run analysis
        print("\nAnalyzing workflow... (this may take a moment)")
        result = await orchestrator.analyze_workflow(workflow_text)

        # Display results
        print("\n" + "=" * 80)
        print("ANALYSIS RESULTS")
        print("=" * 80)

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
        if verbose:
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
        if result.key_insights:
            print(f"\n--- KEY INSIGHTS ---")
            for i, insight in enumerate(result.key_insights, 1):
                print(f"\n[Insight {i}] {insight.title}")
                print(f"  - Priority: {insight.priority}")
                print(f"  - Description: {insight.description}")
                if insight.affected_steps:
                    print(f"  - Affected Steps: {', '.join(insight.affected_steps)}")

        # Recommendations
        if result.recommendations:
            print(f"\n--- RECOMMENDATIONS ---")
            for i, rec in enumerate(result.recommendations, 1):
                print(f"{i}. {rec}")

        # Metrics
        print(f"\n--- METRICS ---")
        metrics = orchestrator.get_analysis_metrics()
        print(f"Total Analyses: {metrics['analyses_total']}")
        print(f"Agent 1 Latency Stats: {metrics['agent_1_parser_latency']}")
        print(f"Agent 2 Latency Stats: {metrics['agent_2_risk_latency']}")
        print(f"Agent 3 Latency Stats: {metrics['agent_3_automation_latency']}")

        # Full JSON output
        if verbose:
            print(f"\n--- FULL JSON OUTPUT ---")
            print(json.dumps(result.dict(), indent=2, default=str))

        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETED SUCCESSFULLY")
        print("=" * 80 + "\n")

        return result

    except Exception as e:
        print(f"\nERROR: Analysis failed: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description='Workflow Analyzer Agent - Analyze workflows with multi-agent system',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m backend                    # Run with default sample workflow
  python -m backend --file workflow.txt # Analyze workflow from file
  python -m backend --workflow "Step 1: Do X\\nStep 2: Do Y"  # Inline workflow
  python -m backend --verbose          # Show detailed analysis
        """
    )

    parser.add_argument(
        '--workflow',
        type=str,
        help='Workflow text to analyze (inline)',
        default=None
    )
    parser.add_argument(
        '--file',
        type=str,
        help='Path to workflow file to analyze',
        default=None
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed analysis output'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )

    args = parser.parse_args()

    # Determine workflow source
    workflow_text = None

    if args.file:
        # Read from file
        try:
            with open(args.file, 'r') as f:
                workflow_text = f.read()
            print(f"Loaded workflow from: {args.file}\n")
        except FileNotFoundError:
            print(f"ERROR: File not found: {args.file}")
            sys.exit(1)

    elif args.workflow:
        # Use provided workflow
        workflow_text = args.workflow

    else:
        # Use default sample workflow
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
        print("Using default sample workflow (customer support workflow)\n")

    # Run analysis
    result = asyncio.run(run_analysis(workflow_text, verbose=args.verbose))

    # Output as JSON if requested
    if args.json:
        print("\n" + "=" * 80)
        print("JSON OUTPUT")
        print("=" * 80 + "\n")
        print(json.dumps(result.dict(), indent=2, default=str))


if __name__ == "__main__":
    main()
