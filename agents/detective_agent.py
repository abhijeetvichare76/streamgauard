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
detective_agent = Agent(
    name="detective",
    model=Gemini(model="gemini-2.0-flash-001", vertexai=True, project=os.getenv("GCP_PROJECT_ID"), location=os.getenv("GCP_REGION")),
    description="The Detective Agent investigates user context, beneficiary risk, and session behavior.",
    instruction=DETECTIVE_INSTRUCTION,
    tools=[user_history_tool, beneficiary_tool, session_context_tool]
)

