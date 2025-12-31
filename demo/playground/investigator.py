"""
Agent investigator for the playground.
Wraps the Detective and Judge agents with real-time callback streaming.
"""

import os
import asyncio
from typing import Callable
from datetime import datetime

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False


def check_vertex_available() -> bool:
    """Check if Vertex AI credentials are available."""
    # Check for project ID
    project_id = None

    if HAS_STREAMLIT and hasattr(st, 'secrets'):
        project_id = st.secrets.get("GCP_PROJECT_ID")
        # Fallback: try to get project_id from service account info
        if not project_id and "gcp_service_account" in st.secrets:
            try:
                project_id = st.secrets["gcp_service_account"].get("project_id")
            except:
                pass

    if not project_id:
        project_id = os.getenv("GCP_PROJECT_ID")

    if not project_id:
        return False

    # Try importing ADK
    try:
        from google.adk import Runner
        from google.adk.sessions import InMemorySessionService
        return True
    except ImportError:
        return False


class PlaygroundInvestigator:
    """
    Runs Detective + Judge agents with real-time event callbacks.
    Uses actual Vertex AI Gemini for reasoning.
    """

    def __init__(self, on_event: Callable[[dict], None]):
        """
        Args:
            on_event: Callback function for real-time updates.
                      Dict format: {"type": "...", "content": "...", ...}
        """
        self.on_event = on_event

    def _emit(self, event_type: str, content: str, **kwargs):
        """Emit an event to the callback."""
        event = {
            "type": event_type,
            "content": content,
            "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
            **kwargs
        }
        if self.on_event:
            self.on_event(event)

    async def investigate_async(self, transaction_data: dict) -> dict:
        """
        Run the full investigation pipeline.

        Args:
            transaction_data: Dict with transaction details + session context

        Returns:
            Dict with 'investigation' and 'judgment' keys
        """
        from google.adk import Runner
        from google.adk.sessions import InMemorySessionService
        from google.genai import types

        # Import agents
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from agents.detective_agent import get_detective_agent
        from agents.judge_agent import get_judge_agent

        # Get agent instances (lazy initialization happens here)
        detective_agent = get_detective_agent()
        judge_agent = get_judge_agent()

        tx_id = transaction_data.get("transaction_id", "pg_unknown")
        user_id = transaction_data.get("user_id", "unknown")

        # Initialize session service
        self._session_service = InMemorySessionService()

        # === DETECTIVE PHASE ===
        self._emit("phase", "DETECTIVE INVESTIGATION")
        self._emit("log", f"Starting investigation for transaction {tx_id}")

        session_id_det = f"pg_det_{tx_id}"
        await self._session_service.create_session(
            app_name="playground",
            user_id="demo",
            session_id=session_id_det
        )

        runner_det = Runner(
            agent=detective_agent,
            session_service=self._session_service,
            app_name="playground"
        )

        # Build investigation prompt with comprehensive fallback data
        customer_profile = transaction_data.get('customer_profile', {})
        beneficiary_data = transaction_data.get('beneficiary_data', {})
        session_data = transaction_data.get('session', {})

        investigation_prompt = f"""Investigate this transaction for potential fraud:

Transaction ID: {tx_id}
User ID: {user_id}
Amount: ${transaction_data.get('amount', 0):.2f}
Beneficiary Account: {transaction_data.get('beneficiary_account_id', 'unknown')}

IMPORTANT: You MUST call all three tools (get_user_history, get_beneficiary_risk, get_session_context) to get the latest data from BigQuery.
The data below is provided ONLY as fallback if the tools return null/empty results.

Fallback Customer Profile:
- User ID: {customer_profile.get('user_id', user_id)}
- Age Group: {customer_profile.get('age_group', 'unknown')}
- Account Tenure: {customer_profile.get('account_tenure_days', 'unknown')} days
- Avg Transfer Amount: ${customer_profile.get('avg_transfer_amount', 0):.2f}
- Behavioral Segment: {customer_profile.get('behavioral_segment', 'unknown')}

Fallback Beneficiary Data:
- Account ID: {beneficiary_data.get('account_id', transaction_data.get('beneficiary_account_id', 'unknown'))}
- Account Age: {beneficiary_data.get('account_age_hours', 'unknown')} hours
- Risk Score: {beneficiary_data.get('risk_score', 'unknown')}
- Linked to Flagged Device: {beneficiary_data.get('linked_to_flagged_device', 'unknown')}

Fallback Session Context:
- Session ID: {session_data.get('session_id', 'unknown')}
- User ID: {session_data.get('user_id', user_id)}
- Is Call Active: {session_data.get('is_call_active', 'unknown')}
- Typing Cadence Score: {session_data.get('typing_cadence_score', 'unknown')}
- Session Duration: {session_data.get('session_duration_seconds', 'unknown')} seconds
- Battery Level: {session_data.get('battery_level', 'unknown')}%
- Device Rooted/Jailbroken: {session_data.get('is_rooted_jailbroken', 'unknown')}
- Time of Day: Hour {session_data.get('time_of_day_hour', 'unknown')}

Use your tools to gather the most up-to-date context. If tools return null, use the fallback data above.
Provide a comprehensive risk assessment following your JSON output format."""

        msg = types.Content(
            role="user",
            parts=[types.Part(text=investigation_prompt)]
        )

        investigation_text = ""
        try:
            async for event in runner_det.run_async(
                user_id="demo",
                session_id=session_id_det,
                new_message=msg
            ):
                # Capture tool calls using the correct ADK methods
                if hasattr(event, 'get_function_calls'):
                    function_calls = event.get_function_calls()
                    if function_calls:
                        for fc in function_calls:
                            tool_name = fc.name if hasattr(fc, 'name') else str(fc)
                            self._emit("log", f"🔧 Detective calling tool: {tool_name}")
                            self._emit(
                                "tool_call",
                                f"Calling {tool_name}",
                                agent="Detective",
                                tool=tool_name,
                                args=str(fc.args)[:200] if hasattr(fc, 'args') else ""
                            )

                if hasattr(event, 'get_function_responses'):
                    function_responses = event.get_function_responses()
                    if function_responses:
                        for fr in function_responses:
                            response_str = str(fr.response)[:300] if hasattr(fr, 'response') else str(fr)[:300]
                            self._emit("log", f"📥 Tool response: {response_str[:100]}...")
                            self._emit(
                                "tool_result",
                                response_str,
                                agent="Detective"
                            )

                # Capture text output
                if event.content:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            investigation_text += part.text
                            # Stream reasoning chunks
                            if len(part.text) > 50:
                                self._emit(
                                    "reasoning",
                                    part.text[:200] + "..." if len(part.text) > 200 else part.text,
                                    agent="Detective"
                                )
        except Exception as e:
            self._emit("error", f"Detective error: {str(e)}")
            investigation_text = f"Investigation failed: {str(e)}"

        self._emit("log", "Detective investigation complete")

        # === JUDGE PHASE ===
        self._emit("phase", "JUDGE DELIBERATION")
        self._emit("log", "Evaluating against policy rules...")

        session_id_judge = f"pg_judge_{tx_id}"
        await self._session_service.create_session(
            app_name="playground",
            user_id="demo",
            session_id=session_id_judge
        )

        runner_judge = Runner(
            agent=judge_agent,
            session_service=self._session_service,
            app_name="playground"
        )

        judgment_prompt = f"""Based on this investigation report, make a decision:

{investigation_text}

Apply the policy rules in priority order and explain your reasoning."""

        msg_judge = types.Content(
            role="user",
            parts=[types.Part(text=judgment_prompt)]
        )

        judgment_text = ""
        try:
            async for event in runner_judge.run_async(
                user_id="demo",
                session_id=session_id_judge,
                new_message=msg_judge
            ):
                if event.content:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            judgment_text += part.text
                            if len(part.text) > 50:
                                self._emit(
                                    "reasoning",
                                    part.text[:200] + "..." if len(part.text) > 200 else part.text,
                                    agent="Judge"
                                )
        except Exception as e:
            self._emit("error", f"Judge error: {str(e)}")
            judgment_text = f"Judgment failed: {str(e)}"

        self._emit("log", "Judge deliberation complete")

        return {
            "investigation": investigation_text,
            "judgment": judgment_text
        }

    def investigate_sync(self, transaction_data: dict) -> dict:
        """Synchronous wrapper for investigate_async."""
        # Try to get existing event loop, create new one only if needed
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                # Loop exists but is closed - create a new one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            # No event loop exists - create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Run investigation - don't close loop to avoid issues on reruns
        return loop.run_until_complete(self.investigate_async(transaction_data))


class SimulatedInvestigator:
    """
    Fallback investigator when Vertex AI is unavailable.
    Returns plausible but canned responses based on input signals.
    """

    def __init__(self, on_event: Callable[[dict], None]):
        self.on_event = on_event

    def _emit(self, event_type: str, content: str, **kwargs):
        import time
        event = {
            "type": event_type,
            "content": content,
            "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
            **kwargs
        }
        if self.on_event:
            self.on_event(event)
        time.sleep(0.2)  # Visual pacing

    def investigate_sync(self, transaction_data: dict) -> dict:
        """Run simulated investigation."""
        import time

        tx_id = transaction_data.get("transaction_id", "pg_unknown")
        user_id = transaction_data.get("user_id", "unknown")
        amount = transaction_data.get("amount", 0)
        session = transaction_data.get("session", {})

        is_call_active = session.get("is_call_active", False)
        is_rooted = session.get("is_rooted_jailbroken", False)
        typing_speed = session.get("typing_cadence_score", 0.5)
        duration = session.get("session_duration_seconds", 120)

        # === DETECTIVE PHASE ===
        self._emit("phase", "DETECTIVE INVESTIGATION (Simulated)")

        self._emit("tool_call", "Calling get_user_history", agent="Detective", tool="get_user_history")
        time.sleep(0.3)
        self._emit("tool_result", f"User {user_id}: Found profile in database", agent="Detective")

        self._emit("tool_call", "Calling get_beneficiary_risk", agent="Detective", tool="get_beneficiary_risk")
        time.sleep(0.3)
        self._emit("tool_result", "Beneficiary risk score retrieved", agent="Detective")

        self._emit("tool_call", "Calling get_session_context", agent="Detective", tool="get_session_context")
        time.sleep(0.3)

        # Highlight critical signals
        if is_call_active:
            self._emit("critical", "ACTIVE VOICE CALL DETECTED", agent="Detective")
        if is_rooted:
            self._emit("warning", "Rooted/jailbroken device detected", agent="Detective")
        if duration < 60:
            self._emit("warning", f"Rushed session: {duration}s", agent="Detective")

        # Calculate simulated risk
        risk_score = 30
        findings = []

        if is_call_active:
            risk_score += 50
            findings.append("Active voice call during transaction")
        if amount > 1000:
            risk_score += 15
            findings.append(f"Large transfer: ${amount:.2f}")
        if is_rooted:
            risk_score += 20
            findings.append("Device is rooted/jailbroken")
        if typing_speed > 0.9:
            risk_score += 10
            findings.append("Abnormally fast typing (possible automation)")
        if typing_speed < 0.3:
            risk_score += 10
            findings.append("Hesitant typing pattern (possible coaching)")
        if duration < 60:
            risk_score += 15
            findings.append("Rushed session duration")

        risk_score = min(risk_score, 100)
        risk_level = "CRITICAL" if risk_score > 80 else "HIGH" if risk_score > 60 else "MEDIUM" if risk_score > 40 else "LOW"
        recommendation = "BLOCK" if risk_score > 70 else "HOLD" if risk_score > 40 else "APPROVE"

        investigation = f"""INVESTIGATION REPORT (SIMULATED)
================================
Transaction ID: {tx_id}
User ID: {user_id}

KEY FINDINGS:
{chr(10).join(f"  - {f}" for f in findings) if findings else "  - No significant risk signals detected"}

RISK ASSESSMENT:
  Risk Score: {risk_score}/100
  Risk Level: {risk_level}

RECOMMENDATION: {recommendation}
"""

        self._emit("reasoning", investigation[:300], agent="Detective")

        # === JUDGE PHASE ===
        self._emit("phase", "JUDGE DELIBERATION (Simulated)")
        time.sleep(0.3)

        # Determine decision based on policies
        if is_call_active:
            decision = "BLOCK"
            policy = "Policy 1: Active Voice Call Override"
            reasoning = "Active voice call detected during transaction. This is a critical fraud signal that overrides other considerations."
        elif risk_score > 70:
            decision = "BLOCK"
            policy = "Policy 2: High Risk Score"
            reasoning = f"Multiple risk signals resulted in score of {risk_score}/100, exceeding BLOCK threshold."
        elif amount < 500 and risk_score < 50:
            decision = "HOLD"
            policy = "Policy 3: First-time + Low Amount"
            reasoning = "Low amount with moderate risk - hold for review rather than block."
        elif risk_score > 40:
            decision = "ESCALATE_TO_HUMAN"
            policy = "Policy 5: Ambiguous Signals"
            reasoning = "Risk signals present but not conclusive. Escalating for human review."
        else:
            decision = "APPROVE"
            policy = "Default: Low Risk"
            reasoning = "No significant risk signals detected. Approving transaction."

        confidence = 95 if is_call_active else 85 if risk_score > 70 else 75

        judgment = f"""JUDGMENT (SIMULATED)
====================
DECISION: {decision}

Policy Applied: {policy}
Confidence: {confidence}%

Reasoning:
{reasoning}

Human Override Allowed: {"NO" if decision == "BLOCK" and is_call_active else "YES"}
"""

        self._emit("reasoning", judgment[:300], agent="Judge")
        self._emit("log", "Judgment complete")

        return {
            "investigation": investigation,
            "judgment": judgment
        }

    async def investigate_async(self, transaction_data: dict) -> dict:
        """Async wrapper for simulated investigation."""
        return self.investigate_sync(transaction_data)
