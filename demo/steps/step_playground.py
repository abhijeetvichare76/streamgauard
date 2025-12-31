"""
Interactive Playground Page.
Single-page layout where judges can build fraud scenarios and watch AI agents investigate.
"""

import streamlit as st
import uuid
from datetime import datetime

# Import playground modules
from playground.presets import PRESETS, apply_preset_to_session_state, get_preset_by_id
from playground.bigquery_operations import (
    check_gcp_available,
    insert_playground_data,
    simulate_insert_all
)
from playground.investigator import (
    check_vertex_available,
    PlaygroundInvestigator,
    SimulatedInvestigator
)
from playground.simulated_enforcer import simulate_enforcement
from playground.enforcer import get_enforcer
from playground.confluent_operations import (
    check_confluent_available,
    produce_transaction,
    consume_alert,
    generate_run_id
)
from playground.components import (
    render_header,
    render_preset_cards,
    render_credentials_warning,
    render_log_container,
    render_report_card,
    render_enforcer_cards,
    render_decision_badge
)


def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        # Logs and results
        "playground_logs": [],
        "investigation_result": None,
        "enforcement_result": None,
        "investigation_running": False,

        # Mode selection - always use real mode with fallback to simulation
        "use_real_confluent": True,

        # Selected preset
        "selected_preset": None,

        # Customer form
        "form_user_id": f"pg_user_{uuid.uuid4().hex[:6]}",
        "form_age_group": "Adult",
        "form_tenure": 365,
        "form_avg_transfer": 100.0,
        "form_segment": "Conservative Saver",

        # Beneficiary form
        "form_acc_id": f"pg_acc_{uuid.uuid4().hex[:6]}",
        "form_acc_age": 720,
        "form_risk_score": 25,
        "form_flagged_device": False,

        # Session form
        "form_call_active": False,
        "form_typing": 0.7,
        "form_duration": 120,
        "form_lat": 40.7128,
        "form_lon": -74.0060,
        "form_hour": 12,
        "form_rooted": False,

        # Transaction form
        "form_amount": 500.0,
        "form_currency": "USD"
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def add_log(log_entry: dict):
    """Add a log entry with timestamp."""
    log_entry["timestamp"] = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    st.session_state.playground_logs.append(log_entry)


def reset_playground():
    """Reset the playground to initial state."""
    st.session_state.playground_logs = []
    st.session_state.investigation_result = None
    st.session_state.enforcement_result = None
    st.session_state.investigation_running = False
    st.session_state.selected_preset = None

    # Note: We don't regenerate form_user_id and form_acc_id here because they're widget keys
    # Users can manually change them or select a new preset to get new values


def run_investigation():
    """Run the full investigation pipeline (real Confluent or simulated)."""
    st.session_state.investigation_running = True
    st.session_state.playground_logs = []
    st.session_state.investigation_result = None
    st.session_state.enforcement_result = None

    # Check credentials
    gcp_ok = check_gcp_available()
    vertex_ok = check_vertex_available()
    confluent_ok = check_confluent_available()
    use_real_confluent = st.session_state.use_real_confluent

    # Generate IDs
    tx_id = f"pg_tx_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:4]}"
    run_id = generate_run_id() if use_real_confluent else None

    # Compile form data
    customer_data = {
        "user_id": st.session_state.form_user_id,
        "age_group": st.session_state.form_age_group,
        "account_tenure_days": st.session_state.form_tenure,
        "avg_transfer_amount": st.session_state.form_avg_transfer,
        "behavioral_segment": st.session_state.form_segment
    }

    beneficiary_data = {
        "account_id": st.session_state.form_acc_id,
        "account_age_hours": st.session_state.form_acc_age,
        "risk_score": st.session_state.form_risk_score,
        "linked_to_flagged_device": st.session_state.form_flagged_device
    }

    session_data = {
        "session_id": f"pg_sess_{uuid.uuid4().hex[:8]}",
        "user_id": st.session_state.form_user_id,
        "event_type": "PLAYGROUND_TEST",
        "is_call_active": st.session_state.form_call_active,
        "typing_cadence_score": st.session_state.form_typing,
        "session_duration_seconds": st.session_state.form_duration,
        "battery_level": 75,
        "app_version": "2.5.0",
        "os_version": "iOS 17.3",
        "is_rooted_jailbroken": st.session_state.form_rooted,
        "geolocation_lat": st.session_state.form_lat,
        "geolocation_lon": st.session_state.form_lon,
        "geolocation_accuracy_meters": 10.0,
        "time_of_day_hour": st.session_state.form_hour,
        "event_time": datetime.utcnow().isoformat()
    }

    transaction_data = {
        "transaction_id": tx_id,
        "user_id": st.session_state.form_user_id,  # For investigator
        "sender_user_id": st.session_state.form_user_id,  # For Kafka schema
        "beneficiary_account_id": st.session_state.form_acc_id,
        "amount": st.session_state.form_amount,
        "currency": st.session_state.form_currency,
        "session_id": session_data["session_id"],
        "first_transfer_to_beneficiary": True,
        "transfer_count_last_hour": 1,
        "device_fingerprint": f"dev_{uuid.uuid4().hex[:8]}",
        "ip_address": "192.168.1.1",
        "geolocation_lat": st.session_state.form_lat,
        "geolocation_lon": st.session_state.form_lon,
        "event_time": int(datetime.utcnow().timestamp() * 1000)
    }

    if run_id:
        transaction_data["playground_run_id"] = run_id

    # ========== CHECK FLINK TRIGGER THRESHOLD ==========
    # Global Flink trigger (fraud_investigation_trigger) requires amount > $1000
    if st.session_state.form_amount < 1000:
        add_log({
            "type": "warning",
            "content": f"⚠️ Amount ${st.session_state.form_amount:.2f} below Flink trigger threshold"
        })
        add_log({
            "type": "info",
            "content": "Global Flink trigger (fraud_investigation_trigger) requires amount > $1000"
        })
        add_log({
            "type": "info",
            "content": "In production, this transaction would NOT be routed to the investigation queue."
        })
        add_log({
            "type": "info",
            "content": "Skipping investigation. Try an amount ≥ $1000 to trigger the full flow."
        })

        # End investigation without running agents
        st.session_state.investigation_running = False
        return

    # ========== REAL CONFLUENT FLOW ==========
    if use_real_confluent and confluent_ok:
        add_log({"type": "phase", "content": "REAL CONFLUENT MODE"})

        # Phase 1: Insert to BigQuery
        add_log({"type": "phase", "content": "DATA INSERTION"})
        if gcp_ok:
            insert_playground_data(customer_data, beneficiary_data, session_data, tx_id, add_log)
        else:
            add_log({"type": "error", "content": "BigQuery not available, falling back to simulation"})
            use_real_confluent = False  # Fall back

        if use_real_confluent:
            # Phase 2: Produce to Kafka
            add_log({"type": "phase", "content": "KAFKA PRODUCE"})
            success = produce_transaction(transaction_data, add_log)

            if not success:
                add_log({"type": "warning", "content": "Kafka produce failed, falling back to simulation"})
                use_real_confluent = False

        if use_real_confluent:
            # Phase 3: Wait for Flink & Consume alert
            add_log({"type": "phase", "content": "FLINK ROUTING & ALERT CONSUMPTION"})
            alert = consume_alert(tx_id, timeout_sec=60, on_progress=add_log)

            if not alert:
                add_log({"type": "warning", "content": "Alert timeout, falling back to simulation"})
                use_real_confluent = False
            else:
                # Phase 4: Run agents on real alert
                add_log({"type": "phase", "content": "AGENT INVESTIGATION"})
                if vertex_ok:
                    investigator = PlaygroundInvestigator(on_event=add_log)
                else:
                    investigator = SimulatedInvestigator(on_event=add_log)

                result = investigator.investigate_sync({
                    "transaction_id": tx_id,
                    **transaction_data,
                    "session": session_data,
                    "customer_profile": customer_data,
                    "beneficiary_data": beneficiary_data
                })
                st.session_state.investigation_result = result

                # Phase 5: Real enforcement
                add_log({"type": "phase", "content": "ENFORCEMENT (REAL RESOURCES)"})
                judgment = result.get("judgment", "")
                decision = "HOLD"
                for d in ["BLOCK", "DENY", "HOLD", "APPROVE", "ESCALATE_TO_HUMAN", "ESCALATE"]:
                    if d in judgment.upper():
                        decision = d
                        break

                enforcer = get_enforcer(use_real_confluent=True)
                enforcement = enforcer.execute(st.session_state.form_user_id, decision, add_log)
                st.session_state.enforcement_result = enforcement

    # ========== FALLBACK OR SIMULATED FLOW ==========
    if not use_real_confluent or not confluent_ok:
        if use_real_confluent and not confluent_ok:
            add_log({"type": "warning", "content": "Confluent not available, using simulation"})

        add_log({"type": "phase", "content": "SIMULATION MODE"})

        # Phase 1: Insert data
        add_log({"type": "phase", "content": "DATA INSERTION"})
        if gcp_ok:
            insert_playground_data(customer_data, beneficiary_data, session_data, tx_id, add_log)
        else:
            simulate_insert_all(customer_data, beneficiary_data, session_data, tx_id, add_log)

        # Phase 2: Run investigation
        add_log({"type": "phase", "content": "AGENT INVESTIGATION"})
        if vertex_ok:
            investigator = PlaygroundInvestigator(on_event=add_log)
        else:
            investigator = SimulatedInvestigator(on_event=add_log)

        tx_for_agents = {
            "transaction_id": tx_id,
            **transaction_data,
            "session": session_data,
            "customer_profile": customer_data,
            "beneficiary_data": beneficiary_data
        }
        result = investigator.investigate_sync(tx_for_agents)
        st.session_state.investigation_result = result

        # Phase 3: Simulated enforcement
        add_log({"type": "phase", "content": "ENFORCER SIMULATION"})
        judgment = result.get("judgment", "")
        decision = "HOLD"
        for d in ["BLOCK", "DENY", "HOLD", "APPROVE", "ESCALATE_TO_HUMAN", "ESCALATE"]:
            if d in judgment.upper():
                decision = d
                break

        enforcer = get_enforcer(use_real_confluent=False)
        enforcement = enforcer.execute(st.session_state.form_user_id, decision, add_log)
        st.session_state.enforcement_result = enforcement

    st.session_state.investigation_running = False


def render():
    """Render the playground page."""
    init_session_state()

    # Header
    render_header()

    # Tutorial recommendation banner
    st.markdown("""
    <div style="background: rgba(255, 193, 7, 0.1); border-left: 4px solid #FFC107; padding: 1.5rem; border-radius: 4px; margin-bottom: 2rem; text-align: center;">
        <p style="color: #FFC107; font-weight: 600; margin: 0 0 0.5rem 0; font-size: 1.1rem;">📚 First time here?</p>
        <p style="color: #C9D1D9; font-size: 0.95rem; margin: 0 0 1rem 0;">
            We highly recommend completing the interactive tutorial first to understand how the AI agents work together to detect fraud.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Tutorial button
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("📖 Start Tutorial", key="playground_start_tutorial", use_container_width=True, type="primary"):
            if st.session_state.app_mode != "Tutorial":
                st.session_state.app_mode = "Tutorial"
                st.session_state.current_step = 0
                st.rerun()

    st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

    # Always use real Confluent mode (fallback to simulation if credentials unavailable)
    confluent_ok = check_confluent_available()
    if 'use_real_confluent' not in st.session_state:
        st.session_state.use_real_confluent = True  # Always try real mode first

    # Check credentials
    gcp_ok = check_gcp_available()
    vertex_ok = check_vertex_available()

    if not gcp_ok or not vertex_ok:
        render_credentials_warning()

    # Preset cards
    clicked_preset = render_preset_cards(PRESETS, st.session_state.selected_preset)
    if clicked_preset:
        preset = get_preset_by_id(clicked_preset)
        if preset:
            apply_preset_to_session_state(preset, st.session_state)
            st.session_state.selected_preset = clicked_preset
            st.rerun()

    # Form section - 2x2 grid
    st.markdown("---")

    col1, col2 = st.columns(2)

    # Customer Profile
    with col1:
        st.markdown('''
        <div style="background: rgba(88, 166, 255, 0.05); border: 2px solid rgba(88, 166, 255, 0.3); border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;">
            <h4 style="color: #58A6FF; margin: 0 0 1rem 0; font-size: 0.95rem; letter-spacing: 1px; text-align: center;">👤 CUSTOMER PROFILE</h4>
        ''', unsafe_allow_html=True)

        st.text_input(
            "User ID",
            key="form_user_id"
        )

        st.selectbox(
            "Age Group",
            ["Young Adult", "Adult", "Senior"],
            key="form_age_group"
        )

        st.number_input(
            "Account Tenure (days)",
            min_value=1, max_value=10000,
            key="form_tenure"
        )

        st.number_input(
            "Avg Transfer Amount ($)",
            min_value=0.01, max_value=100000.0,
            key="form_avg_transfer"
        )

        segments = ["Conservative Saver", "High Volume Trader", "Tech Savvy", "Premium Client", "Vulnerable"]
        st.selectbox(
            "Behavioral Segment",
            segments,
            key="form_segment"
        )

        st.markdown("</div>", unsafe_allow_html=True)

    # Beneficiary
    with col2:
        st.markdown('''
        <div style="background: rgba(210, 153, 34, 0.05); border: 2px solid rgba(210, 153, 34, 0.3); border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;">
            <h4 style="color: #D29922; margin: 0 0 1rem 0; font-size: 0.95rem; letter-spacing: 1px; text-align: center;">🏦 BENEFICIARY</h4>
        ''', unsafe_allow_html=True)

        st.text_input(
            "Account ID",
            value=st.session_state.form_acc_id,
            key="form_acc_id"
        )

        st.number_input(
            "Account Age (hours)",
            min_value=0, max_value=8760,
            value=st.session_state.form_acc_age,
            key="form_acc_age"
        )

        st.slider(
            "Risk Score",
            min_value=0, max_value=100,
            value=st.session_state.form_risk_score,
            key="form_risk_score"
        )

        st.checkbox(
            "Linked to Flagged Device",
            value=st.session_state.form_flagged_device,
            key="form_flagged_device"
        )

        st.markdown("</div>", unsafe_allow_html=True)

    col3, col4 = st.columns(2)

    # Session Context
    with col3:
        st.markdown('''
        <div style="background: rgba(255, 107, 107, 0.05); border: 2px solid rgba(255, 107, 107, 0.3); border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;">
            <h4 style="color: #FF6B6B; margin: 0 0 1rem 0; font-size: 0.95rem; letter-spacing: 1px; text-align: center;">📱 SESSION CONTEXT</h4>
        ''', unsafe_allow_html=True)

        st.checkbox(
            "🚨 ACTIVE VOICE CALL",
            value=st.session_state.form_call_active,
            key="form_call_active",
            help="Critical fraud signal - user is on a phone call during transaction"
        )

        st.slider(
            "Typing Cadence (0=hesitant, 1=confident)",
            min_value=0.0, max_value=1.0,
            value=float(st.session_state.form_typing),
            key="form_typing"
        )

        st.number_input(
            "Session Duration (seconds)",
            min_value=1, max_value=3600,
            value=st.session_state.form_duration,
            key="form_duration"
        )

        col_lat, col_lon = st.columns(2)
        with col_lat:
            st.number_input(
                "Latitude",
                min_value=-90.0, max_value=90.0,
                value=float(st.session_state.form_lat),
                key="form_lat"
            )
        with col_lon:
            st.number_input(
                "Longitude",
                min_value=-180.0, max_value=180.0,
                value=float(st.session_state.form_lon),
                key="form_lon"
            )

        st.slider(
            "Time of Day (hour)",
            min_value=0, max_value=23,
            value=st.session_state.form_hour,
            key="form_hour"
        )

        st.checkbox(
            "Rooted/Jailbroken Device",
            value=st.session_state.form_rooted,
            key="form_rooted"
        )

        st.markdown("</div>", unsafe_allow_html=True)

    # Transaction
    with col4:
        st.markdown('''
        <div style="background: rgba(63, 185, 80, 0.05); border: 2px solid rgba(63, 185, 80, 0.3); border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;">
            <h4 style="color: #3FB950; margin: 0 0 1rem 0; font-size: 0.95rem; letter-spacing: 1px; text-align: center;">💸 TRANSACTION</h4>
        ''', unsafe_allow_html=True)

        st.number_input(
            "Amount ($)",
            min_value=0.01, max_value=1000000.0,
            value=float(st.session_state.form_amount),
            key="form_amount"
        )

        st.selectbox(
            "Currency",
            ["USD", "EUR", "GBP"],
            index=["USD", "EUR", "GBP"].index(st.session_state.form_currency),
            key="form_currency"
        )

        st.markdown("</div>", unsafe_allow_html=True)

    # Run Investigation button - centered below all form sections
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

    # Instructions
    st.markdown("""
    <div style="text-align: center; padding: 1rem; background: rgba(78, 205, 196, 0.05); border-radius: 8px; margin-bottom: 1.5rem;">
        <p style="font-size: 1rem; color: #4ECDC4; margin: 0 0 0.5rem 0; font-weight: 600;">
            Select a preset or customize the fields above, then click RUN INVESTIGATION
        </p>
        <p style="font-size: 0.9rem; color: #8B949E; margin: 0;">
            Watch real AI agents analyze your scenario in real-time
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Run button
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn2:
        run_disabled = st.session_state.investigation_running
        if st.button(
            "🚀 RUN INVESTIGATION",
            type="primary",
            use_container_width=True,
            disabled=run_disabled,
            key="run_button"
        ):
            # Set flag to trigger investigation on next rerun
            st.session_state.investigation_running = True
            st.session_state.playground_logs = []
            st.session_state.investigation_result = None
            st.session_state.enforcement_result = None
            st.rerun()

    # Warning about infrastructure timing
    st.markdown("""
    <div style="background: rgba(255, 193, 7, 0.1); border-left: 4px solid #FFC107; padding: 1rem; border-radius: 4px; margin: 1.5rem 0;">
        <p style="color: #FFC107; font-weight: 600; margin: 0 0 0.5rem 0; font-size: 0.9rem; text-align: center;">⏱️ Real Infrastructure Test</p>
        <p style="color: #C9D1D9; font-size: 0.85rem; margin: 0; text-align: center;">
            This demo runs through actual infrastructure we've built in the backend (Kafka, Flink, BigQuery, Vertex AI).
            Please allow 1-2 minutes for the investigation to complete.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Check if we should run investigation (triggered by button click)
    if st.session_state.get('investigation_running', False) and not st.session_state.investigation_result:
        # Show loading screen first, then run investigation
        run_investigation()
        st.rerun()  # Rerun to show final results

    # Results section
    st.markdown("---")
    st.markdown("""
    <h3 style="text-align: center; color: #4ECDC4; letter-spacing: 3px; margin: 2rem 0;">
        INVESTIGATION RESULTS
    </h3>
    """, unsafe_allow_html=True)

    # Show loading screen OR live log
    if st.session_state.get('investigation_running', False) and not st.session_state.investigation_result:
        # Loading screen while investigation is running
        st.markdown("""
        <div style="text-align: center; padding: 3rem;">
            <div style="display: inline-block; padding: 2rem; background: rgba(78, 205, 196, 0.1); border: 2px solid rgba(78, 205, 196, 0.3); border-radius: 16px;">
                <p style="color: #4ECDC4; font-size: 1.5rem; margin: 0 0 1rem 0; font-weight: 700;">⏳ Investigation in Progress</p>
                <p style="color: #8B949E; font-size: 1rem; margin: 0 0 0.5rem 0;">The AI agents are analyzing your transaction...</p>
                <p style="color: #8B949E; font-size: 0.9rem; margin: 0;">This usually takes about 1 minute. Please wait.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Live Log - always show when there are logs or results
    if st.session_state.playground_logs or st.session_state.investigation_result:
        st.markdown("""
        <div style="background: rgba(78, 205, 196, 0.05); border: 2px solid rgba(78, 205, 196, 0.3); border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem;">
            <h4 style="color: #4ECDC4; margin: 0 0 1rem 0; font-size: 0.95rem; letter-spacing: 1px; text-align: center;">📜 LIVE LOG</h4>
        """, unsafe_allow_html=True)
        if st.session_state.playground_logs:
            render_log_container(st.session_state.playground_logs, max_height=500)
        else:
            st.markdown("<p style='text-align: center; color: #8B949E; font-style: italic;'>Preparing logs...</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Detective and Judge reports
    if st.session_state.investigation_result:
        result = st.session_state.investigation_result

        col_det, col_judge = st.columns(2)

        with col_det:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(88, 166, 255, 0.1) 0%, rgba(78, 205, 196, 0.1) 100%);
                        border: 1px solid rgba(88, 166, 255, 0.3);
                        border-radius: 12px;
                        padding: 1.5rem;
                        margin-bottom: 1.5rem;">
                <h4 style="color: #58A6FF; margin: 0 0 1rem 0; font-size: 1rem; letter-spacing: 2px; text-transform: uppercase;">
                    🔍 DETECTIVE REPORT
                </h4>
            </div>
            """, unsafe_allow_html=True)

            # Extract JSON from markdown code block
            investigation_text = result.get("investigation", "")
            import re
            import json

            # Try to extract JSON from ```json ``` blocks
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', investigation_text, re.DOTALL)
            if json_match:
                try:
                    detective_data = json.loads(json_match.group(1))
                    st.json(detective_data, expanded=True)
                except:
                    st.code(investigation_text, language="json")
            else:
                st.markdown(investigation_text)

        with col_judge:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(255, 107, 107, 0.1) 0%, rgba(210, 153, 34, 0.1) 100%);
                        border: 1px solid rgba(255, 107, 107, 0.3);
                        border-radius: 12px;
                        padding: 1.5rem;
                        margin-bottom: 1.5rem;">
                <h4 style="color: #FF6B6B; margin: 0 0 1rem 0; font-size: 1rem; letter-spacing: 2px; text-transform: uppercase;">
                    ⚖️ JUDGE DECISION
                </h4>
            </div>
            """, unsafe_allow_html=True)

            # Extract JSON from markdown code block
            judgment_text = result.get("judgment", "")

            # Try to extract JSON from ```json ``` blocks
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', judgment_text, re.DOTALL)
            if json_match:
                try:
                    judge_data = json.loads(json_match.group(1))
                    st.json(judge_data, expanded=True)
                except:
                    st.code(judgment_text, language="json")
            else:
                st.markdown(judgment_text)

    # Enforcer results
    if st.session_state.enforcement_result:
        enforcement = st.session_state.enforcement_result

        st.markdown("#### 🛡️ Enforcer Actions")

        # Decision badge
        render_decision_badge(enforcement.get("decision", "UNKNOWN"))

        # Resource cards
        resources = enforcement.get("resources_created", [])
        render_enforcer_cards(resources)

        # Actions taken - Beautiful formatting
        actions = enforcement.get("actions_taken", [])
        if actions:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(78, 205, 196, 0.1) 0%, rgba(88, 166, 255, 0.1) 100%);
                        border: 1px solid rgba(78, 205, 196, 0.3);
                        border-radius: 12px;
                        padding: 1.5rem;
                        margin-top: 1.5rem;">
                <h4 style="color: #4ECDC4; margin: 0 0 1rem 0; font-size: 0.9rem; letter-spacing: 2px; text-transform: uppercase; text-align: center;">
                    🔄 Automated Actions
                </h4>
                <p style="color: #8B949E; margin: 0 0 1rem 0; font-size: 0.85rem; text-align: center;">
                    The following routing rules will be appended to existing Confluent resources for automatic future handling:
                </p>
            """, unsafe_allow_html=True)
            for action in actions:
                st.markdown(f"""
                <div style="background: rgba(0,0,0,0.3);
                            border-left: 3px solid #4ECDC4;
                            border-radius: 6px;
                            padding: 0.75rem 1rem;
                            margin: 0.5rem 0;">
                    <span style="color: #4ECDC4; font-weight: 600;">▸</span>
                    <span style="color: #FAFAFA; margin-left: 0.5rem; font-size: 0.9rem;">{action}</span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # Reset button
    if st.session_state.investigation_result or st.session_state.playground_logs:
        st.markdown("<div style='text-align: center; margin-top: 2rem;'>", unsafe_allow_html=True)
        if st.button("🔄 Reset & Try Another Scenario", key="reset_button"):
            reset_playground()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
