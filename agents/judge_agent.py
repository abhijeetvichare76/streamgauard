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

def get_gcp_config():
    """Get GCP project ID and region from Streamlit secrets or environment."""
    project_id = None
    region = None

    # Try Streamlit secrets first
    try:
        import streamlit as st
        if hasattr(st, 'secrets'):
            project_id = st.secrets.get("GCP_PROJECT_ID")
            region = st.secrets.get("GCP_REGION", "us-central1")
    except (ImportError, Exception):
        pass

    # Fall back to environment variables
    if not project_id:
        project_id = os.getenv("GCP_PROJECT_ID")
    if not region:
        region = os.getenv("GCP_REGION", "us-central1")

    return project_id, region

project_id, region = get_gcp_config()

judge_agent = Agent(
    name="judge",
    model=Gemini(model="gemini-2.0-flash-001", vertexai=True, project=project_id, location=region),
    description="The Judge Agent applies business policies and makes remediation decisions.",
    instruction=JUDGE_INSTRUCTION,
    tools=[]  # Judge uses reasoning, not tools
)

