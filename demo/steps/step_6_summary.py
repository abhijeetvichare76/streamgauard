import streamlit as st

def render():
    st.markdown('<p class="section-label">Demo Complete</p>', unsafe_allow_html=True)
    st.title("Impact Summary: Threat Neutralized")
    st.markdown("<p style='color: #8B949E; font-size: 1.1rem; margin-bottom: 2rem;'>StreamGuard Aegis successfully prevented a $5,000 loss while building a forensic audit trail for law enforcement.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="metric-box" style="border-top: 4px solid #3FB950;">
            <div class="metric-value">$5,000</div>
            <div class="metric-label">Savings Preserved</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-box" style="border-top: 4px solid #58A6FF;">
            <div class="metric-value">< 7s</div>
            <div class="metric-label">Total Response Time</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-box" style="border-top: 4px solid #FF6B6B;">
            <div class="metric-value">100%</div>
            <div class="metric-label">Autonomous Accuracy</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="custom-card" style="margin-top: 3rem;">
        <h4 style="color: #4ECDC4; margin-top:0;">What happened to Betty?</h4>
        <p style="color: #FAFAFA; font-size: 1.1rem; line-height: 1.6;">
            Aegis automatically triggered a "Friendly Hold" on the funds. Betty received an automated SMS & push notification: 
            <i>"We've detected unusual activity on your transfer. A banking specialist will call you in 2 minutes to verify."</i>
        </p>
        <p style="color: #8B949E;">The scammer, seeing the transaction 'processing' but never completing, eventually hung up. Betty's life savings remain intact.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="text-align:center; padding-top: 4rem;">', unsafe_allow_html=True)
    if st.button("Replay Tutorial ↺", type="secondary"):
        st.session_state.current_step = 0
        # Clear triggers
        for key in ['tx_triggered', 'flink_processed', 'investigation_run', 'investigation_complete', 'enforcer_run']:
            if key in st.session_state:
                st.session_state[key] = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="privacy-note" style="margin-top: 5rem;"><b>Privacy & Compliance:</b> All agent reasoning and data sources queried are logged to a tamper-proof BigQuery sink for regulatory review (Financial Conduct Authority compliance).</div>', unsafe_allow_html=True)
