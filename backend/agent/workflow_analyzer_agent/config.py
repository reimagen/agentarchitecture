"""Configuration constants for the workflow analyzer agent."""

# Model Configuration
MODEL = "gemini-2.0-flash-exp"
TEMPERATURE = 0.1  # Low for consistency
TIMEOUT = 30  # seconds

# Workflow Validation
MAX_WORKFLOW_LENGTH = 10000  # characters
MIN_WORKFLOW_LENGTH = 10

# Supported Agent Types
AGENT_TYPES = ["adk_base", "agentic_rag", "TOOL", "HUMAN"]

# Risk Assessment Levels
RISK_LEVELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

# Automation Feasibility Threshold
AUTOMATION_FEASIBLE_THRESHOLD = 0.7

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "json"  # json or text

# Session Configuration
MAX_SESSION_AGE_HOURS = 24
ENABLE_SESSION_PERSISTENCE = False

# Tracing Configuration
ENABLE_DISTRIBUTED_TRACING = True
TRACE_SAMPLE_RATE = 1.0  # 0.0-1.0, 1.0 = trace all

# Metrics Configuration
ENABLE_METRICS = True
METRICS_COLLECTION_INTERVAL_SECONDS = 60
