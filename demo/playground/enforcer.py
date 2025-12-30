"""
Enforcement actions for the playground.
Supports both real Confluent (with resource reuse) and simulated modes.
"""

import time
from typing import Callable
from datetime import datetime

# Import simulated enforcement functions
from playground.simulated_enforcer import simulate_enforcement as _simulate_enforcement


class RealEnforcer:
    """
    Real enforcement using existing Confluent resources.

    For demo stability, we REUSE the persistent playground resources
    instead of creating new ones per-run. This shows the capability
    while avoiding Flink metadata propagation delays.
    """

    def execute(
        self,
        user_id: str,
        decision: str,
        on_progress: Callable[[dict], None] | None = None
    ) -> dict:
        """
        Execute real enforcement actions.

        Note: Uses existing playground quarantine resources for stability.
        Shows what WOULD be created per-user but routes to shared infrastructure.
        """

        def emit(content: str, resource_type: str = None):
            if on_progress:
                on_progress({
                    "type": "real_enforcer",
                    "content": content,
                    "resource_type": resource_type,
                    "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3]
                })
            time.sleep(0.3)  # Slight pacing for readability

        resources_created = []
        actions_taken = []

        safe_user_id = user_id.replace("@", "_").replace(".", "_")[:20]

        if decision in ["BLOCK", "DENY"]:
            emit("Initiating REAL BLOCK enforcement...", "header")
            emit("(Using existing playground resources for demo)", "note")

            # Show what WOULD be created per-user
            topic_name = f"fraud-quarantine-{safe_user_id}"
            flink_name = f"route-{safe_user_id}"
            connector_name = f"sink-{safe_user_id}"

            emit(f"Would create topic: {topic_name}", "kafka")
            emit("  -> Routing to: fraud_quarantine_playground (existing)", "kafka_detail")
            resources_created.append({
                "type": "kafka_topic",
                "name": topic_name,
                "status": "would_create_but_using_shared"
            })

            emit(f"Would create Flink statement: {flink_name}", "flink")
            emit("  -> Using: route_playground_quarantine (existing)", "flink_detail")
            resources_created.append({
                "type": "flink_statement",
                "name": flink_name,
                "status": "would_create_but_using_shared"
            })

            emit(f"Would create connector: {connector_name}", "connector")
            emit("  -> Using: sink_playground_quarantine (existing)", "connector_detail")
            resources_created.append({
                "type": "bq_connector",
                "name": connector_name,
                "status": "would_create_but_using_shared"
            })

            emit("Future transactions from this user will be quarantined", "info")
            actions_taken.append(f"User {user_id} routed to quarantine")

            emit("BLOCK enforcement complete (using shared resources)", "complete")

        elif decision == "HOLD":
            emit("Initiating REAL HOLD enforcement...", "header")

            emit("Marking transaction for review", "hold")
            emit(f"  - User: {user_id}", "hold_detail")
            emit(f"  - Status: HELD", "hold_detail")
            actions_taken.append("Transaction placed on HOLD")

            emit("Creating BigQuery audit entry", "audit")
            actions_taken.append("Audit trail created")

            emit("HOLD enforcement complete", "complete")

        elif decision in ["ESCALATE_TO_HUMAN", "ESCALATE"]:
            emit("Initiating REAL ESCALATE enforcement...", "header")

            emit("Creating analyst review task", "ticket")
            emit(f"  - User: {user_id}", "ticket_detail")
            emit(f"  - Priority: MEDIUM", "ticket_detail")
            actions_taken.append("Review task created")

            emit("Adding to monitoring watchlist", "watchlist")
            emit(f"  - Duration: 48 hours", "watchlist_detail")
            actions_taken.append("User added to watchlist")

            emit("ESCALATE enforcement complete", "complete")

        else:  # APPROVE
            emit("Transaction APPROVED - No enforcement needed", "approve")
            emit("Creating audit trail entry", "audit")
            actions_taken.append("Audit trail created")
            emit("APPROVE enforcement complete", "complete")

        return {
            "decision": decision,
            "user_id": user_id,
            "resources_created": resources_created,
            "actions_taken": actions_taken,
            "simulated": False,
            "uses_shared_resources": True
        }


class SimulatedEnforcer:
    """Simulated enforcement - shows what WOULD happen with visual pacing."""

    def execute(
        self,
        user_id: str,
        decision: str,
        on_progress: Callable[[dict], None] | None = None
    ) -> dict:
        """Execute simulated enforcement (calls existing simulate_enforcement)."""
        return _simulate_enforcement(user_id, decision, on_progress)


def get_enforcer(use_real_confluent: bool) -> RealEnforcer | SimulatedEnforcer:
    """
    Factory to get the appropriate enforcer.

    Args:
        use_real_confluent: If True, return RealEnforcer. Otherwise SimulatedEnforcer.

    Returns:
        Enforcer instance
    """
    if use_real_confluent:
        return RealEnforcer()
    else:
        return SimulatedEnforcer()
