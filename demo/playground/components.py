"""
UI components for the playground page.
Reusable Streamlit components with consistent styling.
"""

import streamlit as st
from datetime import datetime


def render_header():
    """Render the playground header with accurate flow diagram."""
    st.markdown("""
    <div style="text-align: center; padding: 4rem 0 2rem 0;">
        <p style="color: #4ECDC4; font-size: 0.9rem; letter-spacing: 4px; margin-bottom: 0.5rem; text-transform: uppercase; font-weight: 700; opacity: 0.8;">Interactive Demo</p>
        <h1 class="gradient-hero" style="font-size: 3.5rem;">StreamGuard Playground</h1>
        <p class="subtitle" style="font-size: 1.2rem; margin-top: 1rem;">Build your own fraud scenario. Watch the AI swarm react.</p>
    </div>
    """, unsafe_allow_html=True)

    # Pipeline explanation
    st.markdown("""
    <div style="background: rgba(78, 205, 196, 0.05); border: 1px solid rgba(78, 205, 196, 0.2); border-radius: 12px; padding: 2rem; margin: 2rem 0;">
        <div style="text-align: center; margin-bottom: 1.5rem;">
            <span style="color: #4ECDC4; font-size: 0.9rem; letter-spacing: 3px; text-transform: uppercase; font-weight: 700;">How It Works</span>
        </div>
        <div style="color: #C9D1D9; font-size: 0.95rem; line-height: 1.8;">
            <p style="margin-bottom: 1rem;">
                <strong style="color: #4ECDC4;">1. Create your scenario</strong> — Customize the form fields below to simulate different fraud patterns. Transaction data is injected into Kafka (simulating a real mobile banking transaction), while customer profile, beneficiary, and session context are stored in BigQuery for the AI agents to query.
            </p>
            <p style="margin-bottom: 1rem;">
                <strong style="color: #58A6FF;">2. Flink filters high-value transactions</strong> — A Flink SQL statement monitors the Kafka stream and routes transactions above $1,000 to the investigation queue (transactions below this threshold are processed normally without AI review).
            </p>
            <p style="margin-bottom: 1rem;">
                <strong style="color: #FF6B6B;">3. Detective investigates</strong> — The Detective agent pulls context from BigQuery (customer history, beneficiary risk, session behavior) and analyzes the transaction for fraud patterns. Try changing form values to see how different scenarios affect the investigation!
            </p>
            <p style="margin-bottom: 1rem;">
                <strong style="color: #D29922;">4. Judge decides the outcome</strong> — Based on the Detective's findings, the Judge agent renders a decision: APPROVE (safe transaction), BLOCK (clear fraud), or ESCALATE TO HUMAN (uncertain, needs review).
            </p>
            <p style="margin-bottom: 0;">
                <strong style="color: #3FB950;">5. Enforcer builds the infrastructure</strong> — For each decision type, the Enforcer appends routing rules to existing Confluent resources (Kafka topics for alerts, Flink statements for filtering, BigQuery connectors for logging). This ensures similar transactions in the future are automatically handled according to the AI's decision—no manual intervention needed.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_preset_cards(presets: list, selected_id: str | None = None) -> str | None:
    """
    Render preset scenario cards.

    Args:
        presets: List of preset dictionaries
        selected_id: Currently selected preset ID

    Returns:
        ID of clicked preset, or None
    """
    st.markdown("""
    <div style="margin-bottom: 2rem; text-align: center;">
        <h4 class="section-label" style="margin-bottom: 1rem;">Choose a Starting Scenario</h4>
    """, unsafe_allow_html=True)

    cols = st.columns(len(presets))
    clicked_id = None

    icon_map = {
        "phone": "📞",
        "zap": "⚡",
        "git-branch": "🕸️",
        "crown": "👑"
    }

    for i, preset in enumerate(presets):
        with cols[i]:
            is_selected = preset["id"] == selected_id
            
            # Styles for selected vs unselected
            if is_selected:
                border_style = "2px solid #4ECDC4"
                bg_style = "rgba(78, 205, 196, 0.15)"
                transform = "translateY(-5px)"
                box_shadow = "0 8px 25px rgba(78, 205, 196, 0.2)"
            else:
                border_style = "1px solid rgba(255,255,255,0.1)"
                bg_style = "rgba(255,255,255,0.03)"
                transform = "none"
                box_shadow = "none"

            icon = icon_map.get(preset.get("icon", ""), "📋")

            st.markdown(f"""
<div style="
border: {border_style};
background: {bg_style};
backdrop-filter: blur(10px);
border-radius: 16px;
padding: 1.5rem;
text-align: center;
min-height: 160px;
display: flex;
flex-direction: column;
justify-content: center;
transition: all 0.3s ease;
transform: {transform};
box-shadow: {box_shadow};
cursor: default; /* Buttons handle the interaction */
">
<div style="font-size: 2.2rem; margin-bottom: 0.8rem;">{icon}</div>
<div style="color: #FAFAFA; font-weight: 700; font-size: 1rem; margin-bottom: 0.5rem;">{preset["name"]}</div>
<div style="color: #8B949E; font-size: 0.75rem; line-height: 1.4;">{preset["description"]}</div>
</div>
            """, unsafe_allow_html=True)

            if st.button(
                "Select" if not is_selected else "Selected ✓",
                key=f"preset_{preset['id']}",
                use_container_width=True,
                type="primary" if is_selected else "secondary"
            ):
                clicked_id = preset["id"]

    st.markdown("</div>", unsafe_allow_html=True)

    return clicked_id


def render_credentials_warning():
    """Render a warning banner when GCP credentials are unavailable."""
    st.markdown("""
    <div style="background: rgba(255, 193, 7, 0.1); border-left: 4px solid #FFC107; padding: 1rem; border-radius: 4px; margin-bottom: 1.5rem;">
        <p style="color: #FFC107; font-weight: 600; margin: 0 0 0.5rem 0;">⚠️ Running in Simulation Mode</p>
        <p style="color: #8B949E; font-size: 0.85rem; margin: 0;">
            GCP credentials not detected. BigQuery inserts and Vertex AI calls will be simulated.
            The demo will show realistic outputs but won't use real AI reasoning.
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_log_container(logs: list, max_height: int = 300):
    """
    Render a scrolling log container.

    Args:
        logs: List of log entry dicts
        max_height: Maximum height in pixels
    """
    log_html = f'<div class="log-container" style="max-height: {max_height}px; overflow-y: auto; background: #0D1117; border: 1px solid #30363d; border-radius: 8px; padding: 1rem; font-family: monospace; font-size: 0.85rem;">'

    for entry in logs:
        timestamp = entry.get("timestamp", "")
        entry_type = entry.get("type", "log")
        content = entry.get("content", "")
        agent = entry.get("agent", "")

        if entry_type == "phase":
            log_html += f'<div style="color: #4ECDC4; font-weight: 800; margin: 1rem 0; border-top: 1px solid #30363d; padding-top: 0.5rem;">═══ {content} ═══</div>'
        elif entry_type == "tool_call":
            tool = entry.get("tool", "")
            log_html += f'<div><span style="color: #6E7681;">[{timestamp}]</span> <span style="color: #58A6FF;">🔧 {agent}</span> <span style="color: #D29922;">{tool}</span></div>'
        elif entry_type == "tool_result":
            log_html += f'<div style="padding-left: 2rem; color: #8B949E;">{content[:150]}{"..." if len(content) > 150 else ""}</div>'
        elif entry_type == "reasoning":
            color = "#58A6FF" if agent == "Detective" else "#FF6B6B" if agent == "Judge" else "#FAFAFA"
            log_html += f'<div><span style="color: #6E7681;">[{timestamp}]</span> <span style="color: {color};">{agent}:</span> {content[:200]}{"..." if len(content) > 200 else ""}</div>'
        elif entry_type == "critical":
            log_html += f'<div style="color: #FF6B6B; font-weight: 600;"><span style="color: #6E7681;">[{timestamp}]</span> 🚨 {content}</div>'
        elif entry_type == "warning":
            log_html += f'<div style="color: #D29922;"><span style="color: #6E7681;">[{timestamp}]</span> ⚠️ {content}</div>'
        elif entry_type == "success":
            log_html += f'<div style="color: #3FB950;"><span style="color: #6E7681;">[{timestamp}]</span> ✅ {content}</div>'
        elif entry_type in ["bq_insert", "simulated_bq"]:
            log_html += f'<div style="color: #58A6FF;"><span style="color: #6E7681;">[{timestamp}]</span> 💾 {content}</div>'
        elif entry_type == "simulated":
            resource_type = entry.get("resource_type", "")
            if resource_type == "header":
                log_html += f'<div style="color: #4ECDC4; margin-top: 0.5rem;"><span style="color: #6E7681;">[{timestamp}]</span> {content}</div>'
            elif resource_type == "complete":
                log_html += f'<div style="color: #3FB950; font-weight: 600;"><span style="color: #6E7681;">[{timestamp}]</span> ✅ {content}</div>'
            elif "_detail" in str(resource_type):
                log_html += f'<div style="padding-left: 2rem; color: #8B949E;">{content}</div>'
            else:
                log_html += f'<div style="color: #FCD34D;"><span style="color: #6E7681;">[{timestamp}]</span> [SIMULATED] {content}</div>'
        elif entry_type == "error":
            log_html += f'<div style="color: #FF6B6B;"><span style="color: #6E7681;">[{timestamp}]</span> ❌ {content}</div>'
        else:
            log_html += f'<div><span style="color: #6E7681;">[{timestamp}]</span> {content}</div>'

    log_html += '</div>'

    st.markdown(log_html, unsafe_allow_html=True)


def render_report_card(title: str, content: str, icon: str = "📋", border_color: str = "#58A6FF"):
    """
    Render a report card with formatted content.

    Args:
        title: Card title
        content: Card content (can include newlines)
        icon: Emoji icon
        border_color: Border color for themed styling
    """
    # Escape HTML and convert newlines
    safe_content = content.replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")

    # Styling colors based on common roles
    if "DETECTIVE" in title.upper():
        header_color = "#58A6FF"
        bg_color = "rgba(88, 166, 255, 0.05)"
        border_style = "2px solid rgba(88, 166, 255, 0.3)"
    elif "JUDGE" in title.upper():
        header_color = "#FF6B6B"
        bg_color = "rgba(255, 107, 107, 0.05)"
        border_style = "2px solid rgba(255, 107, 107, 0.3)"
    elif "ENFORCER" in title.upper():
        header_color = "#4ECDC4"
        bg_color = "rgba(78, 205, 196, 0.05)"
        border_style = "2px solid rgba(78, 205, 196, 0.3)"
    else:
        header_color = "#FAFAFA"
        bg_color = "rgba(255, 255, 255, 0.05)"
        border_style = f"2px solid {border_color}"

    st.markdown(f"""
<div style="background: {bg_color}; border: {border_style}; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem;">
    <h4 style="color: {header_color}; margin: 0 0 1rem 0; font-size: 0.95rem; letter-spacing: 1px; text-align: center;">
        <span style="font-size: 1.2rem;">{icon}</span> {title}
    </h4>
    <div style="color: #C9D1D9; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; line-height: 1.6;">
        {safe_content}
    </div>
</div>
    """, unsafe_allow_html=True)


def render_enforcer_cards(resources: list):
    """
    Render Enforcer infrastructure cards.

    Args:
        resources: List of resource dicts from simulated_enforcer
    """
    if not resources:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; color: #8B949E;">
            No infrastructure resources to create for this decision.
        </div>
        """, unsafe_allow_html=True)
        return

    cols = st.columns(len(resources))

    icon_map = {
        "kafka_topic": "📨",
        "flink_statement": "⚡",
        "bq_connector": "💾"
    }

    color_map = {
        "kafka_topic": "#4ECDC4",
        "flink_statement": "#9B59B6",
        "bq_connector": "#58A6FF"
    }

    label_map = {
        "kafka_topic": "Kafka Topic",
        "flink_statement": "Flink Route",
        "bq_connector": "BQ Connector"
    }

    for i, resource in enumerate(resources):
        with cols[i]:
            r_type = resource.get("type", "unknown")
            r_name = resource.get("name", "unnamed")
            icon = icon_map.get(r_type, "📦")
            color = color_map.get(r_type, "#8B949E")
            label = label_map.get(r_type, r_type)

            st.markdown(f"""
            <div style="
                background: rgba(0,0,0,0.3);
                border: 1px solid {color};
                border-radius: 10px;
                padding: 1.5rem;
                text-align: center;
            ">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
                <div style="color: {color}; font-weight: 600; font-size: 0.85rem; letter-spacing: 1px;">{label}</div>
                <div style="color: #FAFAFA; font-family: monospace; font-size: 0.75rem; margin-top: 0.5rem; word-break: break-all;">{r_name}</div>
                <div style="color: #4ECDC4; font-size: 0.7rem; margin-top: 0.5rem;">[APPEND ROUTING RULE]</div>
            </div>
            """, unsafe_allow_html=True)


def render_decision_badge(decision: str):
    """Render a large decision badge."""
    color_map = {
        "BLOCK": "#FF6B6B",
        "DENY": "#FF6B6B",
        "HOLD": "#D29922",
        "ESCALATE_TO_HUMAN": "#9B59B6",
        "ESCALATE": "#9B59B6",
        "APPROVE": "#3FB950"
    }

    # Icon map for decisions
    icon_map = {
        "BLOCK": "🚫",
        "DENY": "🚫",
        "HOLD": "⏸️",
        "ESCALATE_TO_HUMAN": "🆘",
        "ESCALATE": "⬆️",
        "APPROVE": "✅"
    }

    color = color_map.get(decision, "#8B949E")
    icon = icon_map.get(decision, "❓")
    # Remove underscores and make it more readable
    display_text = decision.replace("_", " ")

    st.markdown(f"""
    <div style="text-align: center; margin: 2rem 0;">
        <div style="
            display: inline-block;
            background: {color};
            color: #0E1117;
            padding: 1rem 2.5rem;
            border-radius: 12px;
            font-weight: 800;
            font-size: 1.4rem;
            letter-spacing: 2px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        ">
            <span style="font-size: 1.6rem; margin-right: 0.5rem;">{icon}</span>
            {display_text}
        </div>
    </div>
    """, unsafe_allow_html=True)
