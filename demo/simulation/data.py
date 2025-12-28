BETTY_TRANSACTION = {
    "transaction_id": "tx_betty_5000_001",
    "sender_user_id": "betty_senior",
    "beneficiary_account_id": "acc_scammer_new",
    "amount": 5000.00,
    "currency": "USD",
    "session_id": "sess_coached_001",
    "first_transfer": True,
    "velocity": "1 in last hour",
    "device": "iPhone 12, iOS 17"
}

INVESTIGATION_REPORT = {
    "user_profile": "Betty, 75, Conservative Saver. 10-year customer, typical transfer $50. This: $5,000 (100x).",
    "beneficiary_risk": "Account created 2 hours ago. Linked to flagged devices. Risk: 95/100.",
    "session_behavior": "🚨 Active phone call. 🚨 Rushed session. 🚨 200 miles away.",
    "risk_score": "98/100",
    "recommendation": "BLOCK"
}

AUDIT_RECORD = {
    "transaction_id": "tx_betty_5000_001",
    "decision": "BLOCK",
    "policy_applied": "active_voice_call_override",
    "risk_score": 98,
    "infrastructure": "fraud-quarantine-betty-senior",
    "timestamp": "2025-12-27T10:30:10Z"
}
