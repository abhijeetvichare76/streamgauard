import streamlit as st
import time

def render():
    st.markdown('<p class="section-label">Step 3 of 6</p>', unsafe_allow_html=True)
    st.title("Detective Agent Investigates")
    st.markdown("<p style='color: #8B949E; font-size: 1.1rem; margin-bottom: 2rem;'>The Detective Agent performs a multi-dimensional investigation, querying real BigQuery datasets to reconstruct the full context of the transaction.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-box" style="border-bottom: 4px solid #58A6FF; height: 100%;"><div class="metric-label">Who is Betty?</div><div style="font-size: 0.85rem; color: #FAFAFA; margin-top:0.5rem;">[BigQuery]<br>customer_profiles</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-box" style="border-bottom: 4px solid #D29922; height: 100%;"><div class="metric-label">Recipient Risk?</div><div style="font-size: 0.85rem; color: #FAFAFA; margin-top:0.5rem;">[BigQuery]<br>beneficiary_graph</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-box" style="border-bottom: 4px solid #F85149; height: 100%;"><div class="metric-label">Device Context?</div><div style="font-size: 0.85rem; color: #FAFAFA; margin-top:0.5rem;">[BigQuery]<br>sessions</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

    if st.button("Run Investigation →", type="primary", disabled=st.session_state.get('investigation_run', False)):
        st.session_state.investigation_run = True
        st.rerun()

    if st.session_state.get('investigation_run', False):
        if 'investigation_complete' not in st.session_state:
            with st.status("🕵️ Swarm Investigation in Progress...", expanded=True) as status:
                st.write("Fetching customer data...")
                time.sleep(1)
                st.markdown('<span style="color: #3FB950;">✅ Found: 10yr loyalty, low-velocity profile</span>', unsafe_allow_html=True)
                
                st.write("Analyzing beneficiary graph...")
                time.sleep(1)
                st.markdown('<span style="color: #D29922;">⚠️ Target account created 2h ago (High Risk)</span>', unsafe_allow_html=True)
                
                st.write("Checking session telemetry...")
                time.sleep(1)
                st.markdown('<span style="color: #F85149;">🚨 Telemetry: On active voice call (Coaching Signature)</span>', unsafe_allow_html=True)
                
                status.update(label="Investigation Finalized", state="complete")
            st.session_state.investigation_complete = True

        st.markdown("""
        <div class="custom-card">
            <h4 style="margin-top:0; color: #58A6FF; letter-spacing: 1px;">🕵️ DETECTIVE'S FORENSIC REPORT</h4>
            <div style="background: rgba(0,0,0,0.3); padding: 2rem; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); margin-top: 1.5rem;">
                <p style="color: #FAFAFA; font-size: 1.1rem; border-left: 3px solid #58A6FF; padding-left: 1rem; margin-bottom: 1.5rem;">
                    <b>Subject:</b> Betty (USR_7421) - Profile anomaly detected. User typically transfers <$50. Current activity: <b>$5,000.00</b> (10,000% deviation).
                </p>
                <p style="color: #D29922; margin-bottom: 1rem;">Target account is linked to a cluster of recent fraud alerts. Recipient age: <b>124 minutes</b>.</p>
                <p style="color: #F85149; font-weight: 600;">CRITICAL: Real-time session data confirms user is navigating banking app while on a phone call. Social engineering signature confirmed.</p>
                <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.1); margin: 2rem 0;">
                <div style="display:flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 1.4rem; font-weight:900; color: #FAFAFA;">SWARM RISK INDEX: <span style="color: #F85149;">98%</span></span>
                    <span style="background: #F85149; color: #FAFAFA; padding: 6px 15px; border-radius: 6px; font-weight:800; font-size: 0.9rem;">ESCALATE TO JUDGE</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Next: Judge Decision →"):
            st.session_state.current_step = 4
            st.rerun()
