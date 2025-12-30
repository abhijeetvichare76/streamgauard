import streamlit as st

def render():
    st.markdown('<p class="section-label">Step 1 of 6</p>', unsafe_allow_html=True)
    st.title("A Transaction Arrives")
    st.markdown("<p style='color: #8B949E; font-size: 1.1rem; margin-bottom: 2rem;'>When Betty initiates a bank transfer, these signals are captured and streamed to Confluent Kafka in real-time.</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="custom-card" style="height: 100%;">
            <h4 style="color: #4ECDC4; margin-top: 0; margin-bottom: 1.5rem;">Transaction Payload</h4>
            <table style="width:100%; color: #FAFAFA; border-spacing: 0 10px; border-collapse: separate;">
                <tr><td><b>TX ID</b></td><td style="text-align:right; color: #8B949E; font-family: 'JetBrains Mono';">tx_betty_5000_001</td></tr>
                <tr><td><b>From</b></td><td style="text-align:right; color: #8B949E;">Betty Senior (USR_7421)</td></tr>
                <tr><td><b>To Account</b></td><td style="text-align:right; color: #8B949E;">ACC_SCAMMER_NEW</td></tr>
                <tr><td><b>Amount</b></td><td style="text-align:right; color: #4ECDC4; font-weight:800; font-size: 1.2rem;">$5,000.00</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="custom-card" style="height: 100%;">
            <h4 style="color: #FF6B6B; margin-top: 0; margin-bottom: 1.5rem;">Meta Signals</h4>
            <table style="width:100%; color: #FAFAFA; border-spacing: 0 10px; border-collapse: separate;">
                <tr><td><b>Session ID</b></td><td style="text-align:right; color: #8B949E; font-family: 'JetBrains Mono';">sess_coached_99</td></tr>
                <tr><td><b>First Transfer?</b></td><td style="text-align:right; color: #F85149; font-weight: 700;">YES ⚠️</td></tr>
                <tr><td><b>IP Velocity</b></td><td style="text-align:right; color: #8B949E;">1 in last hour</td></tr>
                <tr><td><b>Device</b></td><td style="text-align:right; color: #8B949E;">iPhone 12 (iOS 17)</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background: rgba(78, 205, 196, 0.05); border-left: 4px solid #4ECDC4; padding: 1rem; border-radius: 4px; margin-bottom: 1rem;'>
        <p style='color: #FAFAFA; margin: 0 0 0.5rem 0; font-weight: 600;'>What happens next?</p>
        <p style='color: #8B949E; margin: 0;'>
            Betty's transaction will be published to the <code style='color: #4ECDC4;'>customer_bank_transfers</code> Kafka topic.
            A Flink SQL statement continuously monitors this stream, filtering for high-value transfers that need AI review.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Send Transaction →", type="primary", disabled=st.session_state.get('tx_triggered', False)):
        st.session_state.tx_triggered = True
        st.rerun()

    if st.session_state.get('tx_triggered', False):
        st.markdown("""
            <div class="log-container">
                <div class="log-entry"><span class="log-info">[10:30:01]</span> 📤 Producing Avro message to <b>customer_bank_transfers</b>...</div>
                <div class="log-entry" style="padding-left: 1rem; color: #8B949E; font-size: 0.8rem;">{ "tx_id": "tx_betty_5000_001", "amount": 5000, "meta": "..." }</div>
                <div class="log-entry"><span class="log-success">[10:30:01]</span> ✅ Message delivered successfully (Cluster: GCP-West-1, Partition: 3)</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div style="height: 30px;"></div>', unsafe_allow_html=True)
        if st.button("Next: Flink Trigger →"):
            st.session_state.current_step = 2
            st.rerun()
