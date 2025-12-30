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

def get_gcp_config():
    """Get GCP project ID and region from Streamlit secrets or environment."""
    project_id = None
    region = None

    # Try Streamlit secrets first
    try:
        import streamlit as st
        if hasattr(st, 'secrets'):
            # Set up authentication for Vertex AI if service account is available
            if "gcp_service_account" in st.secrets:
                # Write service account to temp file and set GOOGLE_APPLICATION_CREDENTIALS
                service_account_info = dict(st.secrets["gcp_service_account"])

                # Create a temporary file for the service account key
                temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
                json.dump(service_account_info, temp_file)
                temp_file.close()

                # Set the environment variable that google-cloud libraries use
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = temp_file.name

            # Get project and region
            project_id = st.secrets.get("GCP_PROJECT_ID") or st.secrets.get("gcp_project_id")
            region = st.secrets.get("GCP_REGION") or st.secrets.get("gcp_region") or "us-central1"
    except (ImportError, Exception) as e:
        # Silently pass - will fall back to env vars
        pass

    # Fall back to environment variables
    if not project_id:
        project_id = os.getenv("GCP_PROJECT_ID")
    if not region:
        region = os.getenv("GCP_REGION", "us-central1")

    return project_id, region

# Lazy initialization - only create agent when first accessed
_detective_agent_instance = None

def get_detective_agent():
    """Get or create the detective agent instance (lazy initialization)."""
    global _detective_agent_instance
    if _detective_agent_instance is None:
        project_id, region = get_gcp_config()
        _detective_agent_instance = Agent(
            name="detective",
            model=Gemini(model="gemini-2.0-flash-001", vertexai=True, project=project_id, location=region),
            description="The Detective Agent investigates user context, beneficiary risk, and session behavior.",
            instruction=DETECTIVE_INSTRUCTION,
            tools=[user_history_tool, beneficiary_tool, session_context_tool]
        )
    return _detective_agent_instance

# For backward compatibility - auto-initialize when imported directly
detective_agent = None  # Will be None until get_detective_agent() is called

