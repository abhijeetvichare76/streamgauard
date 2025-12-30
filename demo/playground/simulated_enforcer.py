"""
Simulated Confluent infrastructure actions.
Shows what WOULD be created without making real API calls.
"""

import time
from typing import Callable
from datetime import datetime


def simulate_enforcement(
    user_id: str,
    decision: str,
    on_progress: Callable[[dict], None] | None = None
) -> dict:
    """
    Simulate Confluent infrastructure creation without real API calls.

    Args:
        user_id: User ID for naming resources
        decision: Judge's decision (BLOCK, HOLD, APPROVE, ESCALATE_TO_HUMAN)
        on_progress: Callback for progress updates

    Returns:
        Dict with simulated resource information
    """

    def emit(content: str, resource_type: str = None):
        if on_progress:
            on_progress({
                "type": "simulated",
                "content": content,
                "resource_type": resource_type,
                "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3]
            })
        time.sleep(0.4)  # Visual pacing

    resources_created = []
    actions_taken = []

    # Sanitize user_id for resource naming
    safe_user_id = user_id.replace("@", "_").replace(".", "_")[:20]

    if decision in ["BLOCK", "DENY"]:
        emit("Initiating BLOCK enforcement sequence...", "header")

        # 1. Create quarantine topic
        topic_name = f"fraud-quarantine-{safe_user_id}"
        emit(f"Creating Kafka topic: {topic_name}", "kafka")
        emit(f"  - Partitions: 3", "kafka_detail")
        emit(f"  - Retention: 7 days", "kafka_detail")
        emit(f"  - Schema: fraud_quarantine.avsc", "kafka_detail")
        resources_created.append({
            "type": "kafka_topic",
            "name": topic_name,
            "icon": "database"
        })

        # 2. Deploy Flink routing statement
        flink_name = f"route-{safe_user_id}"
        emit(f"Deploying Flink SQL statement: {flink_name}", "flink")
        emit(f"  - Source: customer_bank_transfers", "flink_detail")
        emit(f"  - Filter: user_id = '{user_id}'", "flink_detail")
        emit(f"  - Target: {topic_name}", "flink_detail")
        resources_created.append({
            "type": "flink_statement",
            "name": flink_name,
            "icon": "zap"
        })

        # 3. Create BigQuery sink connector
        connector_name = f"sink-{safe_user_id}"
        emit(f"Creating BigQuery connector: {connector_name}", "connector")
        emit(f"  - Source topic: {topic_name}", "connector_detail")
        emit(f"  - Target table: streamguard_threats.quarantine_{safe_user_id}", "connector_detail")
        emit(f"  - Auto-create table: enabled", "connector_detail")
        resources_created.append({
            "type": "bq_connector",
            "name": connector_name,
            "icon": "database"
        })

        # 4. Send Slack notification
        emit("Sending Slack alert to #security-ops", "notification")
        emit(f"  - Priority: HIGH", "notification_detail")
        emit(f"  - User flagged: {user_id}", "notification_detail")
        emit(f"  - Infrastructure created: 3 resources", "notification_detail")
        actions_taken.append("Slack alert sent to #security-ops")

        emit("BLOCK enforcement complete - User isolated", "complete")

    elif decision == "HOLD":
        emit("Initiating HOLD enforcement sequence...", "header")

        # Hold doesn't create infrastructure, just logs and notifies
        emit("Transaction placed on HOLD", "hold")
        emit(f"  - User: {user_id}", "hold_detail")
        emit(f"  - Status: Pending Review", "hold_detail")
        emit(f"  - Timeout: 24 hours", "hold_detail")
        actions_taken.append("Transaction marked as HELD")

        emit("Creating audit trail entry in BigQuery", "audit")
        actions_taken.append("Audit trail created")

        emit("Sending notification to fraud-review queue", "notification")
        actions_taken.append("Review request queued")

        emit("HOLD enforcement complete - Awaiting review", "complete")

    elif decision in ["ESCALATE_TO_HUMAN", "ESCALATE"]:
        emit("Initiating ESCALATE enforcement sequence...", "header")

        # Create ServiceNow ticket
        emit("Creating ServiceNow incident ticket", "ticket")
        emit(f"  - Priority: MEDIUM", "ticket_detail")
        emit(f"  - Assigned to: Fraud Analysts", "ticket_detail")
        emit(f"  - SLA: 4 hours", "ticket_detail")
        actions_taken.append("ServiceNow ticket created")

        # Slack to analysts
        emit("Sending Slack alert to #fraud-analysts", "notification")
        emit(f"  - User: {user_id}", "notification_detail")
        emit(f"  - Reason: Ambiguous risk signals", "notification_detail")
        actions_taken.append("Analyst notification sent")

        # Create watchlist entry
        emit("Adding user to temporary watchlist", "watchlist")
        emit(f"  - Duration: 48 hours", "watchlist_detail")
        emit(f"  - Monitoring: All transactions", "watchlist_detail")
        actions_taken.append("User added to watchlist")

        emit("ESCALATE enforcement complete - Human review initiated", "complete")

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
        "simulated": True
    }


def get_enforcement_summary(enforcement_result: dict) -> str:
    """Get a human-readable summary of enforcement actions."""
    decision = enforcement_result.get("decision", "UNKNOWN")
    resources = enforcement_result.get("resources_created", [])
    actions = enforcement_result.get("actions_taken", [])

    summary_lines = [f"Decision: {decision}"]

    if resources:
        summary_lines.append(f"Resources that would be created: {len(resources)}")
        for r in resources:
            summary_lines.append(f"  - {r['type']}: {r['name']}")

    if actions:
        summary_lines.append(f"Actions that would be taken: {len(actions)}")
        for a in actions:
            summary_lines.append(f"  - {a}")

    return "\n".join(summary_lines)
