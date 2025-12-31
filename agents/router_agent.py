"""The Router Agent - Orchestrates the agent swarm."""
import asyncio
import json
import re
from typing import Dict, Any, Optional
from pydantic import ValidationError

from google.adk.agents import Agent
from google.adk.models import Gemini
from google.adk import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types

from agents.detective_agent import get_detective_agent
from agents.judge_agent import get_judge_agent
from agents.enforcer_agent import enforcer_agent
from agents.liaison_agent import liaison_agent
from config.models import InvestigationReport, JudgmentDecision
from config.gcp_credentials import setup_gcp_credentials
from config.validation import (
    validate_investigation_completeness,
    validate_judgment_policy,
    AgentValidationError,
    ToolCallError
)

# Helper functions for agent response processing

def _get_text(events):
    """Extract text from Runner events."""
    text = ""
    for event in events:
        if event.content:
            for part in event.content.parts:
                if part.text:
                    text += part.text
    return text


def _extract_json(text: str) -> Optional[Dict[str, Any]]:
    """Extract JSON from agent response text.

    Handles cases where JSON is wrapped in markdown code blocks or has extra text.

    Args:
        text: Raw text response from agent

    Returns:
        Parsed JSON dict, or None if parsing fails
    """
    # Try to extract JSON from markdown code blocks
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        # Try to find raw JSON object
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
        else:
            return None

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Attempted to parse: {json_str[:200]}...")
        return None


def _validate_investigation(data: Dict[str, Any]) -> Optional[InvestigationReport]:
    """Validate investigation data against Pydantic model.

    Args:
        data: Raw JSON data from Detective agent

    Returns:
        Validated InvestigationReport, or None if validation fails
    """
    try:
        return InvestigationReport(**data)
    except ValidationError as e:
        print(f"Investigation validation error: {e}")
        return None


def _validate_judgment(data: Dict[str, Any]) -> Optional[JudgmentDecision]:
    """Validate judgment data against Pydantic model.

    Args:
        data: Raw JSON data from Judge agent

    Returns:
        Validated JudgmentDecision, or None if validation fails
    """
    try:
        return JudgmentDecision(**data)
    except ValidationError as e:
        print(f"Judgment validation error: {e}")
        return None

# Sequential workflow for threat processing
class ThreatProcessingWorkflow:
    """
    Orchestrates the Detective -> Judge -> Enforcer pipeline with structured communication.

    This workflow:
    1. Detective investigates (with parallel tool calls)
    2. Validates Detective output against Pydantic model
    3. Judge makes decision based on structured investigation
    4. Validates Judge output against Pydantic model
    5. Enforcer executes the decision
    """

    def __init__(self):
        """Initialize workflow with lazy-loaded agents."""
        # Initialize agents using getter functions (lazy initialization)
        self._detective = None
        self._judge = None
        self.enforcer = enforcer_agent
        self.session_service = InMemorySessionService()
        self.app_name = "streamguard"

    @property
    def detective(self):
        """Lazy-load detective agent."""
        if self._detective is None:
            self._detective = get_detective_agent()
        return self._detective

    @property
    def judge(self):
        """Lazy-load judge agent."""
        if self._judge is None:
            self._judge = get_judge_agent()
        return self._judge

    async def process_threat_async(self, threat_data: dict) -> dict:
        """Process a threat through the full agent pipeline with structured communication.

        Args:
            threat_data: Raw threat data from Kafka/Flink

        Returns:
            dict containing:
                - investigation: InvestigationReport (Pydantic model)
                - investigation_text: Human-readable summary
                - judgment: JudgmentDecision (Pydantic model)
                - judgment_text: Human-readable summary
                - execution: Enforcer output text
                - errors: List of any errors encountered

        Raises:
            ValueError: If critical validation fails
        """
        user_id = "system"
        transaction_id = threat_data.get('transaction_id')
        errors = []

        # ====================
        # Step 1: Detective investigates
        # ====================
        print(f"[Detective] Starting investigation for {transaction_id}")
        session_id_det = f"det_{transaction_id}"

        try:
            await self.session_service.create_session(
                app_name=self.app_name,
                user_id=user_id,
                session_id=session_id_det
            )
            runner_det = Runner(
                agent=self.detective,
                session_service=self.session_service,
                app_name=self.app_name
            )

            msg_det = types.Content(
                role="user",
                parts=[types.Part(text=f"Investigate this transaction:\n{json.dumps(threat_data, indent=2)}")]
            )

            events_det = []
            async for event in runner_det.run_async(
                user_id=user_id,
                session_id=session_id_det,
                new_message=msg_det
            ):
                events_det.append(event)

            investigation_text = _get_text(events_det)
            print(f"[Detective] Raw response length: {len(investigation_text)} chars")

            # Parse and validate JSON output
            investigation_json = _extract_json(investigation_text)
            if not investigation_json:
                error_msg = f"Detective failed to return valid JSON for {transaction_id}"
                errors.append(error_msg)
                raise ValueError(error_msg)

            investigation_report = _validate_investigation(investigation_json)
            if not investigation_report:
                error_msg = f"Detective output failed validation for {transaction_id}"
                errors.append(error_msg)
                raise ValueError(error_msg)

            # Validate that all required tools were called
            try:
                validate_investigation_completeness(investigation_report)
            except ToolCallError as e:
                error_msg = f"Detective tool validation failed: {str(e)}"
                errors.append(error_msg)
                print(f"[Detective] WARNING: {error_msg}")
                # Don't raise - continue with partial data but log the issue

            print(f"[Detective] Investigation complete - Risk: {investigation_report.risk_level.value}")

        except Exception as e:
            error_msg = f"Detective agent error: {str(e)}"
            errors.append(error_msg)
            print(f"[Detective] ERROR: {error_msg}")
            raise

        # ====================
        # Step 2: Judge makes decision
        # ====================
        print(f"[Judge] Evaluating investigation for {transaction_id}")
        session_id_judge = f"judge_{transaction_id}"

        try:
            await self.session_service.create_session(
                app_name=self.app_name,
                user_id=user_id,
                session_id=session_id_judge
            )
            runner_judge = Runner(
                agent=self.judge,
                session_service=self.session_service,
                app_name=self.app_name
            )

            # Pass structured investigation as JSON
            msg_judge = types.Content(
                role="user",
                parts=[types.Part(text=f"Based on this investigation, make a decision:\n```json\n{investigation_report.model_dump_json(indent=2)}\n```")]
            )

            events_judge = []
            async for event in runner_judge.run_async(
                user_id=user_id,
                session_id=session_id_judge,
                new_message=msg_judge
            ):
                events_judge.append(event)

            judgment_text = _get_text(events_judge)
            print(f"[Judge] Raw response length: {len(judgment_text)} chars")

            # Parse and validate JSON output
            judgment_json = _extract_json(judgment_text)
            if not judgment_json:
                error_msg = f"Judge failed to return valid JSON for {transaction_id}"
                errors.append(error_msg)
                raise ValueError(error_msg)

            judgment_decision = _validate_judgment(judgment_json)
            if not judgment_decision:
                error_msg = f"Judge output failed validation for {transaction_id}"
                errors.append(error_msg)
                raise ValueError(error_msg)

            # Validate policy application consistency
            try:
                validate_judgment_policy(judgment_decision, investigation_report)
            except AgentValidationError as e:
                error_msg = f"Judge policy validation warning: {str(e)}"
                errors.append(error_msg)
                print(f"[Judge] WARNING: {error_msg}")
                # Don't raise - LLM may have valid reasoning for deviation

            print(f"[Judge] Decision: {judgment_decision.decision.value} (Policy #{judgment_decision.policy_applied})")

        except Exception as e:
            error_msg = f"Judge agent error: {str(e)}"
            errors.append(error_msg)
            print(f"[Judge] ERROR: {error_msg}")
            raise

        # ====================
        # Step 3: Enforcer executes
        # ====================
        print(f"[Enforcer] Executing decision for {transaction_id}")
        session_id_enf = f"enf_{transaction_id}"

        try:
            await self.session_service.create_session(
                app_name=self.app_name,
                user_id=user_id,
                session_id=session_id_enf
            )
            runner_enf = Runner(
                agent=self.enforcer,
                session_service=self.session_service,
                app_name=self.app_name
            )

            msg_enf = types.Content(
                role="user",
                parts=[types.Part(text=f"Execute this judgment:\n{judgment_decision.to_text_summary()}\n\nTransaction ID: {transaction_id}")]
            )

            events_enf = []
            async for event in runner_enf.run_async(
                user_id=user_id,
                session_id=session_id_enf,
                new_message=msg_enf
            ):
                events_enf.append(event)

            execution_text = _get_text(events_enf)
            print(f"[Enforcer] Execution complete")

        except Exception as e:
            error_msg = f"Enforcer agent error: {str(e)}"
            errors.append(error_msg)
            print(f"[Enforcer] ERROR: {error_msg}")
            # Don't raise here - we still want to return investigation/judgment

        # Return structured results
        return {
            "investigation": investigation_report,
            "investigation_text": investigation_report.to_text_summary(),
            "judgment": judgment_decision,
            "judgment_text": judgment_decision.to_text_summary(),
            "execution": execution_text,
            "errors": errors
        }

    def process_threat(self, threat_data: dict) -> dict:
        """Sync wrapper for process_threat_async."""
        return asyncio.run(self.process_threat_async(threat_data))


import os

# Chat router for human interaction (lazy initialization)
_chat_router_instance = None

def get_chat_router():
    """Get or create the chat router agent (lazy initialization).

    Returns:
        Agent: The chat router configured with sub-agents
    """
    global _chat_router_instance
    if _chat_router_instance is None:
        # Set up credentials
        project_id, region = setup_gcp_credentials()

        # Initialize chat router with sub-agents
        _chat_router_instance = Agent(
            name="streamguard_chat",
            model=Gemini(
                model="gemini-2.0-flash-001",
                vertexai=True,
                project=project_id,
                location=region
            ),
            sub_agents=[get_detective_agent(), liaison_agent],
            instruction="""
            Route user requests:
            - Questions about specific users/transactions -> detective
            - General questions, explanations, admin commands -> liaison
            - "Why was X blocked?" -> detective first, then liaison to explain
            """
        )
    return _chat_router_instance

# For backward compatibility
chat_router = None  # Will be None until get_chat_router() is called
