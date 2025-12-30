import streamlit as st
import time

def render():
    st.markdown('<p class="section-label">Step 2 of 6</p>', unsafe_allow_html=True)
    st.title("Flink SQL: Real-Time Trigger")
    st.markdown("<p style='color: #8B949E; font-size: 1.1rem; margin-bottom: 2rem;'>Confluent Cloud Flink continuously monitors the <code>customer_bank_transfers</code> stream. When the system detects a high-value transfer, it triggers an investigation alert and notifies the Agent Swarm.</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="custom-card">
        <h4 style="color: #4ECDC4; margin-top:0; margin-bottom:1.5rem;">Flink SQL Statement</h4>
        <div style="background: #0D1117; padding: 1.5rem; border-radius: 10px; border: 1px solid #30363d; font-family: 'JetBrains Mono', monospace; font-size: 0.95rem; line-height: 1.6;">
            <span style="color: #C678DD;">INSERT INTO</span> <span style="color: #98C379;">fraud_investigation_queue</span><br>
            <span style="color: #C678DD;">SELECT</span> * <span style="color: #C678DD;">FROM</span> <span style="color: #98C379;">customer_bank_transfers</span><br>
            <span style="color: #C678DD;">WHERE</span> amount > <span style="color: #D19A66;">1000.00</span>;
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<p style='color: #8B949E;'>Betty's <b>$5,000.00</b> transfer significantly exceeds our threshold for deep context investigation.</p>", unsafe_allow_html=True)

    if 'flink_processed' not in st.session_state:
        st.session_state.flink_processed = False

    st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

    if not st.session_state.flink_processed:
        if st.button("Run Flink Processing →", type="primary"):
            st.session_state.flink_processed = True
            st.rerun()
    else:
        with st.status("Flink Stream Processing...", expanded=True) as status:
            st.write("🔎 Monitoring stream: customer_bank_transfers")
            time.sleep(0.8)
            st.write("🎯 Match found! Amount $5000.00 exceeds threshold of $1000.00")
            time.sleep(0.5)
            st.markdown('<span style="color: #3FB950;">✅ Alert published to fraud_investigation_queue</span>', unsafe_allow_html=True)
            st.write("🤖 ADK Agent Swarm (Detective Agent) subscribed to alert...")
            status.update(label="Event-Driven Alert Fired", state="complete")

        st.markdown("""
            <div class="log-container">
                <div class="log-entry"><span class="log-info">[10:30:02]</span> ⚡ <b>Flink Engine:</b> High-Value Activity Detected! (amount=5000)</div>
                <div class="log-entry"><span class="log-success">[10:30:02]</span> ✅ Record routed to <b>fraud_investigation_queue</b></div>
                <div class="log-entry"><span class="log-info">[10:30:02]</span> 📢 Notify Swarm: Investigator Agent requested for betty_senior</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="height: 30px;"></div>', unsafe_allow_html=True)
        if st.button("Next: Detective Agent →"):
            st.session_state.current_step = 3
            st.rerun()
