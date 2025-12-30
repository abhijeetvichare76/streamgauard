"""
Preset fraud scenarios for the playground.
Each preset defines a complete test case with expected outcome.
"""

PRESETS = [
    {
        "id": "coaching",
        "name": "Classic Coaching",
        "icon": "phone",
        "description": "Elderly victim coached over phone. Active call + rushed session.",
        "customer": {
            "user_id": "pg_betty_senior",
            "age_group": "Senior",
            "account_tenure_days": 3650,
            "avg_transfer_amount": 50.0,
            "behavioral_segment": "Conservative Saver"
        },
        "beneficiary": {
            "account_id": "pg_acc_scammer_new",
            "account_age_hours": 2,
            "risk_score": 95,
            "linked_to_flagged_device": True
        },
        "session": {
            "is_call_active": True,
            "typing_cadence_score": 0.25,
            "session_duration_seconds": 35,
            "geolocation_lat": 45.5,
            "geolocation_lon": -122.5,
            "time_of_day_hour": 3,
            "is_rooted_jailbroken": False
        },
        "transaction": {
            "amount": 5000.0,
            "currency": "USD"
        },
        "expected_outcome": "BLOCK",
        "expected_policy": "Policy 1: Active Voice Call Override"
    },
    {
        "id": "velocity",
        "name": "Velocity Attack",
        "icon": "zap",
        "description": "Rooted device, suspiciously fast typing, first-time offense.",
        "customer": {
            "user_id": "pg_hacker_001",
            "age_group": "Young Adult",
            "account_tenure_days": 180,
            "avg_transfer_amount": 200.0,
            "behavioral_segment": "Tech Savvy"
        },
        "beneficiary": {
            "account_id": "pg_acc_target_normal",
            "account_age_hours": 8760,
            "risk_score": 15,
            "linked_to_flagged_device": False
        },
        "session": {
            "is_call_active": False,
            "typing_cadence_score": 0.95,
            "session_duration_seconds": 5,
            "geolocation_lat": 40.7,
            "geolocation_lon": -74.0,
            "time_of_day_hour": 14,
            "is_rooted_jailbroken": True
        },
        "transaction": {
            "amount": 250.0,
            "currency": "USD"
        },
        "expected_outcome": "HOLD",
        "expected_policy": "Policy 3: First-time + under $500"
    },
    {
        "id": "mule",
        "name": "Mule Network",
        "icon": "git-branch",
        "description": "Repeat offender sending to newly created flagged account.",
        "customer": {
            "user_id": "pg_mule_repeat",
            "age_group": "Adult",
            "account_tenure_days": 90,
            "avg_transfer_amount": 1500.0,
            "behavioral_segment": "High Volume Trader"
        },
        "beneficiary": {
            "account_id": "pg_acc_mule_endpoint",
            "account_age_hours": 6,
            "risk_score": 88,
            "linked_to_flagged_device": True
        },
        "session": {
            "is_call_active": False,
            "typing_cadence_score": 0.7,
            "session_duration_seconds": 120,
            "geolocation_lat": 41.0,
            "geolocation_lon": -73.5,
            "time_of_day_hour": 22,
            "is_rooted_jailbroken": False
        },
        "transaction": {
            "amount": 2500.0,
            "currency": "USD"
        },
        "expected_outcome": "BLOCK",
        "expected_policy": "Policy 2: Repeat Offender"
    },
    {
        "id": "vip",
        "name": "VIP Edge Case",
        "icon": "crown",
        "description": "20-year premium customer with ambiguous signals. Tests escalation.",
        "customer": {
            "user_id": "pg_vip_platinum",
            "age_group": "Senior",
            "account_tenure_days": 7300,
            "avg_transfer_amount": 5000.0,
            "behavioral_segment": "Premium Client"
        },
        "beneficiary": {
            "account_id": "pg_acc_new_charity",
            "account_age_hours": 12,
            "risk_score": 45,
            "linked_to_flagged_device": False
        },
        "session": {
            "is_call_active": False,
            "typing_cadence_score": 0.5,
            "session_duration_seconds": 180,
            "geolocation_lat": 40.8,
            "geolocation_lon": -74.1,
            "time_of_day_hour": 10,
            "is_rooted_jailbroken": False
        },
        "transaction": {
            "amount": 10000.0,
            "currency": "USD"
        },
        "expected_outcome": "ESCALATE_TO_HUMAN",
        "expected_policy": "Policy 5: VIP Protection"
    }
]


def get_preset_by_id(preset_id: str) -> dict | None:
    """Get a preset by its ID."""
    for preset in PRESETS:
        if preset["id"] == preset_id:
            return preset
    return None


def apply_preset_to_session_state(preset: dict, session_state) -> None:
    """Apply a preset's values to Streamlit session state."""
    # Customer fields
    session_state.form_user_id = preset["customer"]["user_id"]
    session_state.form_age_group = preset["customer"]["age_group"]
    session_state.form_tenure = preset["customer"]["account_tenure_days"]
    session_state.form_avg_transfer = preset["customer"]["avg_transfer_amount"]
    session_state.form_segment = preset["customer"]["behavioral_segment"]

    # Beneficiary fields
    session_state.form_acc_id = preset["beneficiary"]["account_id"]
    session_state.form_acc_age = preset["beneficiary"]["account_age_hours"]
    session_state.form_risk_score = preset["beneficiary"]["risk_score"]
    session_state.form_flagged_device = preset["beneficiary"]["linked_to_flagged_device"]

    # Session fields
    session_state.form_call_active = preset["session"]["is_call_active"]
    session_state.form_typing = preset["session"]["typing_cadence_score"]
    session_state.form_duration = preset["session"]["session_duration_seconds"]
    session_state.form_lat = preset["session"]["geolocation_lat"]
    session_state.form_lon = preset["session"]["geolocation_lon"]
    session_state.form_hour = preset["session"]["time_of_day_hour"]
    session_state.form_rooted = preset["session"]["is_rooted_jailbroken"]

    # Transaction fields
    session_state.form_amount = preset["transaction"]["amount"]
    session_state.form_currency = preset["transaction"]["currency"]
