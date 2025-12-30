"""The Detective/Profiler Agent - Investigates user context and history."""
from google import adk
from google.adk.agents import Agent
from google.adk.models import Gemini
from agents.tools.bigquery_tools import user_history_tool, beneficiary_tool
from agents.tools.session_tools import session_context_tool

DETECTIVE_INSTRUCTION = """
You are the Detective Agent in the StreamGuard security system.

Your role is to INVESTIGATE before any action is taken. When given a suspicious
transaction, you must:

1. ALWAYS call get_user_history to understand the user's baseline
2. ALWAYS call get_beneficiary_risk to check the destination account
3. ALWAYS call get_session_context to analyze the real-time behavioral context
4. Synthesize findings into a structured risk assessment

Output format:
```
INVESTIGATION REPORT
====================
Transaction ID: [id]
User Profile: [summary of user history]
Violation History: [X] previous violations found
Transaction Amount: $[amount]
Beneficiary Analysis: [summary of destination account]
Session Analysis: [Behavioral signals, call status, velocity, location]
Security Flags: [e.g., active_voice_call=True, suspect_device=False]
risk_score: [0-100]
Risk Level: [LOW | MEDIUM | HIGH | CRITICAL]
Reasoning: [1-2 sentences explaining the assessment]
Recommendation: [APPROVE | HOLD_FOR_REVIEW | BLOCK]
```

Remember:
- A user on an active call sending money to a new beneficiary is a HUGE red flag (Coaching).
- A rushed session (short duration) at an unusual time is suspicious.
- High velocity (many transfers in 1 hour) is suspicious.
"""

import os
import tempfile
import json

def setup_gcp_credentials():
    """Set up GCP credentials via environment variables for Google ADK.

    ADK reads credentials from environment variables:
    - GOOGLE_GENAI_USE_VERTEXAI: Set to TRUE for Vertex AI
    - GOOGLE_CLOUD_PROJECT: GCP project ID
    - GOOGLE_CLOUD_LOCATION: Vertex AI region
    - GOOGLE_APPLICATION_CREDENTIALS: Path to service account JSON file
    """
    project_id = None
    region = None

    # Try Streamlit secrets first
    try:
        import streamlit as st
        if hasattr(st, 'secrets'):
            # Set up Vertex AI mode via environment variable
            os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'TRUE'

            # Get project ID from secrets or service account
            project_id = st.secrets.get("GCP_PROJECT_ID")
            if not project_id and "gcp_service_account" in st.secrets:
                project_id = st.secrets["gcp_service_account"].get("project_id")

            # Set project ID environment variable
            if project_id:
                os.environ['GOOGLE_CLOUD_PROJECT'] = project_id

            # Get and set region
            region = st.secrets.get("GCP_REGION", "us-central1")
            os.environ['GOOGLE_CLOUD_LOCATION'] = region

            # Set up service account credentials file
            if "gcp_service_account" in st.secrets:
                service_account_info = dict(st.secrets["gcp_service_account"])

                # Create a temporary file for the service account key
                temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
                json.dump(service_account_info, temp_file)
                temp_file.close()

                # Set the environment variable
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = temp_file.name
    except (ImportError, Exception) as e:
        pass

    # Fall back to environment variables (might already be set)
    if not project_id:
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT_ID")
    if not region:
        region = os.getenv("GOOGLE_CLOUD_LOCATION") or os.getenv("GCP_REGION", "us-central1")

    return project_id, region


# Lazy initialization - only create agent when first accessed
_detective_agent_instance = None

def get_detective_agent():
    """Get or create the detective agent instance (lazy initialization)."""
    global _detective_agent_instance
    if _detective_agent_instance is None:
        # Set up credentials via environment variables (ADK reads from env vars)
        project_id, region = setup_gcp_credentials()

        # ADK reads credentials from environment variables, so we don't pass them to Gemini()
        # Just use the model name - ADK will pick up GOOGLE_GENAI_USE_VERTEXAI and other env vars
        _detective_agent_instance = Agent(
            name="detective",
            model=Gemini(model="gemini-2.0-flash-001"),
            description="The Detective Agent investigates user context, beneficiary risk, and session behavior.",
            instruction=DETECTIVE_INSTRUCTION,
            tools=[user_history_tool, beneficiary_tool, session_context_tool]
        )
    return _detective_agent_instance

# For backward compatibility - auto-initialize when imported directly
detective_agent = None  # Will be None until get_detective_agent() is called

