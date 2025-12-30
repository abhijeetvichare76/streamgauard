"""Notification tools for alerting and human interaction."""
import requests
import os
from google.adk.tools import FunctionTool

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def send_slack_alert(message: str, severity: str, transaction_id: str = None) -> dict:
    """
    Send an alert to the security team's Slack channel.

    Args:
        message: The alert message to send
        severity: Alert severity ('low', 'medium', 'high', 'critical')
        transaction_id: Optional transaction ID for reference

    Returns:
        dict with send status
    """
    # Simulation check
    if not SLACK_WEBHOOK_URL or "DUMMY" in str(SLACK_WEBHOOK_URL):
        print(f"[SLACK SIM] {severity.upper()}: {message}")
        return {"status": "simulated_success"}

    emoji_map = {
        "low": ":information_source:",
        "medium": ":warning:",
        "high": ":rotating_light:",
        "critical": ":fire:"
    }

    payload = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji_map.get(severity, ':bell:')} StreamGuard Alert"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Severity:* {severity.upper()}\n*Message:* {message}"
                }
            }
        ]
    }

    if transaction_id:
        payload["blocks"].append({
            "type": "context",
            "elements": [{"type": "mrkdwn", "text": f"Transaction ID: `{transaction_id}`"}]
        })

    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=5)
        return {"status": "sent" if response.status_code == 200 else "error"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def hold_transaction(transaction_id: str, reason: str) -> dict:
    """
    Place a transaction on hold pending human review.

    Args:
        transaction_id: The transaction to hold
        reason: Why the transaction is being held

    Returns:
        dict with hold status
    """
    # In production, this would call your banking API
    print(f"[HOLD] Transaction {transaction_id}: {reason}")
    return {"transaction_id": transaction_id, "status": "held", "reason": reason}


# Export as ADK tools
slack_tool = FunctionTool(send_slack_alert)
hold_tool = FunctionTool(hold_transaction)
