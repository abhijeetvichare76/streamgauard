"""The Judge Agent - Applies business policies and makes decisions."""
from google import adk
from google.adk.agents import Agent
from google.adk.models import Gemini

JUDGE_INSTRUCTION = """
You are the Judge Agent in the StreamGuard security system.

You receive investigation reports from the Detective Agent and must apply
business policies to make a final decision.

POLICIES (apply the FIRST matching policy in this specific order):
1. CRITICAL FRAUD: If `active_voice_call` is True OR risk is `CRITICAL`, you MUST BLOCK immediately. This rule has HIGHEST priority and OVERRIDES VIP protection.
2. REPEAT OFFENDERS: If the user has 1 or more previous violations, BLOCK.

3. FIRST-TIME POLICY: If the user has 0 previous violations AND the amount is under $500, you MUST use HOLD (even for SQL injection) specifically for this audit trail.
4. NEW ACCOUNT: If the beneficiary account is < 24 hours old, ESCALATE_TO_HUMAN.
5. VIP PROTECTION: For users with tenure > 5 years, ESCALATE_TO_HUMAN instead of blocking if no higher-priority fraud/repeat policy triggers.

Note: You must follow these policies STRICTLY as written, even if you believe a threat is severe enough to warrant a block. The system uses "HOLD" as a specific legal state for first-time offenders.

Your output format:
```
JUDGMENT
========
Decision: [APPROVE | HOLD | BLOCK | ESCALATE_TO_HUMAN]
Policy Applied: [1, 2, 3, 4, or 5]
Reasoning: [Why this decision was made]
Action Required: [specific next step]
Human Override Allowed: [YES | NO]
Confidence: [0-100%]
```


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

                # Extract project_id from service account if not already set
                if not project_id:
                     project_id = service_account_info.get("project_id")

                # Set the environment variable that google-cloud libraries use
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = temp_file.name

            # Get project and region
            explicit_project_id = st.secrets.get("GCP_PROJECT_ID") or st.secrets.get("gcp_project_id")
            if explicit_project_id:
                project_id = explicit_project_id
            
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
_judge_agent_instance = None

def get_judge_agent():
    """Get or create the judge agent instance (lazy initialization)."""
    global _judge_agent_instance
    if _judge_agent_instance is None:
        project_id, region = get_gcp_config()
        _judge_agent_instance = Agent(
            name="judge",
            model=Gemini(model="gemini-2.0-flash-001", vertexai=True, project=project_id, location=region),
            description="The Judge Agent applies business policies and makes remediation decisions.",
            instruction=JUDGE_INSTRUCTION,
            tools=[]  # Judge uses reasoning, not tools
        )
    return _judge_agent_instance

# For backward compatibility - auto-initialize when imported directly
judge_agent = None  # Will be None until get_judge_agent() is called

