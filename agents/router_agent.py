"""The Router Agent - Orchestrates the agent swarm."""
import asyncio
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.adk import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types

from agents.detective_agent import detective_agent
from agents.judge_agent import judge_agent
from agents.enforcer_agent import enforcer_agent
from agents.liaison_agent import liaison_agent

# Local helper to get response text from Runner events
def _get_text(events):
    text = ""
    for event in events:
        if event.content:
            for part in event.content.parts:
                if part.text:
                    text += part.text
    return text

# Sequential workflow for threat processing
class ThreatProcessingWorkflow:
    """
    Orchestrates the Detective -> Judge -> Enforcer pipeline.
    """

    def __init__(self):
        self.detective = detective_agent
        self.judge = judge_agent
        self.enforcer = enforcer_agent
        self.session_service = InMemorySessionService()
        self.app_name = "streamguard"

    async def process_threat_async(self, threat_data: dict) -> dict:
        """Process a threat through the full agent pipeline."""
        user_id = "system"
        
        # Step 1: Detective investigates
        session_id_det = f"det_{threat_data.get('transaction_id')}"
        await self.session_service.create_session(app_name=self.app_name, user_id=user_id, session_id=session_id_det)
        runner_det = Runner(agent=self.detective, session_service=self.session_service, app_name=self.app_name)
        
        msg_det = types.Content(role="user", parts=[types.Part(text=f"Investigate this transaction:\n{threat_data}")])
        events_det = []
        async for event in runner_det.run_async(user_id=user_id, session_id=session_id_det, new_message=msg_det):
            events_det.append(event)
        investigation_text = _get_text(events_det)

        # Step 2: Judge makes decision
        session_id_judge = f"judge_{threat_data.get('transaction_id')}"
        await self.session_service.create_session(app_name=self.app_name, user_id=user_id, session_id=session_id_judge)
        runner_judge = Runner(agent=self.judge, session_service=self.session_service, app_name=self.app_name)
        
        msg_judge = types.Content(role="user", parts=[types.Part(text=f"Based on this investigation, make a decision:\n{investigation_text}")])
        events_judge = []
        async for event in runner_judge.run_async(user_id=user_id, session_id=session_id_judge, new_message=msg_judge):
            events_judge.append(event)
        judgment_text = _get_text(events_judge)

        # Step 3: Enforcer executes
        session_id_enf = f"enf_{threat_data.get('transaction_id')}"
        await self.session_service.create_session(app_name=self.app_name, user_id=user_id, session_id=session_id_enf)
        runner_enf = Runner(agent=self.enforcer, session_service=self.session_service, app_name=self.app_name)
        
        msg_enf = types.Content(role="user", parts=[types.Part(text=f"Execute this judgment:\n{judgment_text}\n\nTransaction ID: {threat_data.get('transaction_id')}")])
        events_enf = []
        async for event in runner_enf.run_async(user_id=user_id, session_id=session_id_enf, new_message=msg_enf):
            events_enf.append(event)
        execution_text = _get_text(events_enf)

        return {
            "investigation": investigation_text,
            "judgment": judgment_text,
            "execution": execution_text
        }

    def process_threat(self, threat_data: dict) -> dict:
        """Sync wrapper for process_threat_async."""
        return asyncio.run(self.process_threat_async(threat_data))


import os

# Chat router for human interaction
chat_router = Agent(
    name="streamguard_chat",
    model=Gemini(model="gemini-2.0-flash-001", vertexai=True, project=os.getenv("GCP_PROJECT_ID"), location=os.getenv("GCP_REGION")),
    sub_agents=[detective_agent, liaison_agent],
    instruction="""
    Route user requests:
    - Questions about specific users/transactions -> detective
    - General questions, explanations, admin commands -> liaison
    - "Why was X blocked?" -> detective first, then liaison to explain
    """
)
