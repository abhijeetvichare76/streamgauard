import streamlit as st
import time
from components.diagrams import render_infrastructure_flow

def render():
    st.markdown('<p class="section-label">Step 5 of 6</p>', unsafe_allow_html=True)
    st.title("🛡️ Enforcer: Autonomous Isolation")
    st.markdown("<p style='color: #8B949E; font-size: 1.1rem; margin-bottom: 2rem;'>The Enforcer Agent doesn't just alert—it autonomously creates quarantine infrastructure in real-time.</p>", unsafe_allow_html=True)
    
    # Introduction section
    st.markdown("""
    <div class="custom-card" style="background: rgba(78, 205, 196, 0.05); border-left: 4px solid #4ECDC4; margin-bottom: 2rem;">
        <p style="color: #FAFAFA; font-size: 1.1rem; margin: 0;">
            <b>This is where StreamGuard differs from traditional systems.</b>
        </p>
        <p style="color: #8B949E; font-size: 0.95rem; margin-top: 0.5rem; margin-bottom: 0;">
            Most systems just flag suspicious transactions. StreamGuard autonomously creates quarantine infrastructure.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.get('enforcer_run', False):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Execute Enforcement →", type="primary", use_container_width=True):
                st.session_state.enforcer_run = True
                st.rerun()
    else:
        # Enforcement Log
        enforcement_html = """<div class="custom-card" style="background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1);"><h4 style="color: #4ECDC4; margin-top:0; margin-bottom:1.5rem;">⚙️ Enforcement Log</h4><div class="log-container" style="background: transparent; border: none; padding: 0;"><div class="log-entry"><span class="log-info">[10:30:06]</span> 🔧 Creating Kafka topic...</div><div class="log-entry"><span class="log-success">✅</span> Topic: <code style="color: #4ECDC4;">fraud-quarantine-betty-senior</code></div><div class="log-entry" style="margin-top: 1rem;"><span class="log-info">[10:30:07]</span> 🔧 Deploying Flink routing statement...</div><div class="log-entry"><span class="log-success">✅</span> Statement: <code style="color: #4ECDC4;">route-betty-senior</code> (RUNNING)</div><div class="log-entry" style="padding-left: 2rem; color: #8B949E;">All future transfers from Betty → quarantine</div><div class="log-entry" style="margin-top: 1rem;"><span class="log-info">[10:30:09]</span> 🔧 Creating BigQuery connector...</div><div class="log-entry"><span class="log-success">✅</span> Connector: <code style="color: #4ECDC4;">sink-betty-senior</code> (RUNNING)</div><div class="log-entry" style="padding-left: 2rem; color: #8B949E;">Quarantined transactions → audit table</div><div class="log-entry" style="margin-top: 1rem;"><span class="log-info">[10:30:10]</span> 📢 Sending Slack alert...</div><div class="log-entry"><span class="log-success">✅</span> Security team notified</div></div></div>"""
        st.markdown(enforcement_html, unsafe_allow_html=True)
        
        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
        
        # Infrastructure Created
        st.markdown("""
        <div class="custom-card">
            <h4 style="color: #58A6FF; margin-top:0; margin-bottom:2rem;">📦 Infrastructure Created</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Infrastructure Flow Diagram
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            st.markdown("""
            <div class="infra-card" style="background: rgba(88, 166, 255, 0.1); border: 2px solid #58A6FF; border-radius: 12px; padding: 1.5rem; text-align: center; height: 220px; display: flex; flex-direction: column; justify-content: center; position: relative; cursor: pointer; transition: all 0.3s ease;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📨</div>
                <p style="color: #58A6FF; font-weight: 700; margin: 0.5rem 0;">Kafka Topic</p>
                <p style="color: #FAFAFA; font-size: 0.9rem; margin: 0.5rem 0;"><code>fraud-quarantine-betty-senior</code></p>
                <p style="color: #8B949E; font-size: 0.8rem; margin: 0;">Partitions: 3</p>
                <div class="tooltip" style="border: 1px solid #58A6FF;">
                    <p style="color: #58A6FF; font-weight: 700; font-size: 0.75rem; margin: 0 0 0.5rem 0;">WHY THIS RESOURCE?</p>
                    <p style="color: #C9D1D9; font-size: 0.75rem; margin: 0; line-height: 1.4;">Dedicated quarantine topic isolates Betty's transactions from normal processing, enabling separate audit trail and preventing fraud propagation.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="infra-card" style="background: rgba(155, 89, 182, 0.1); border: 2px solid #9B59B6; border-radius: 12px; padding: 1.5rem; text-align: center; height: 220px; display: flex; flex-direction: column; justify-content: center; position: relative; cursor: pointer; transition: all 0.3s ease;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">⚡</div>
                <p style="color: #9B59B6; font-weight: 700; margin: 0.5rem 0;">Flink Statement</p>
                <p style="color: #FAFAFA; font-size: 0.9rem; margin: 0.5rem 0;"><code>route-betty-senior</code></p>
                <p style="color: #8B949E; font-size: 0.8rem; margin: 0;">Status: RUNNING</p>
                <div class="tooltip" style="border: 1px solid #9B59B6;">
                    <p style="color: #9B59B6; font-weight: 700; font-size: 0.75rem; margin: 0 0 0.5rem 0;">WHY THIS RESOURCE?</p>
                    <p style="color: #C9D1D9; font-size: 0.75rem; margin: 0; line-height: 1.4;">Real-time routing statement intercepts ALL future transactions from Betty and redirects them to the quarantine topic before they can be processed.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div class="infra-card" style="background: rgba(78, 205, 196, 0.1); border: 2px solid #4ECDC4; border-radius: 12px; padding: 1.5rem; text-align: center; height: 220px; display: flex; flex-direction: column; justify-content: center; position: relative; cursor: pointer; transition: all 0.3s ease;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">💾</div>
                <p style="color: #4ECDC4; font-weight: 700; margin: 0.5rem 0;">BigQuery Sink</p>
                <p style="color: #FAFAFA; font-size: 0.9rem; margin: 0.5rem 0;"><code>sink-betty-senior</code></p>
                <p style="color: #8B949E; font-size: 0.8rem; margin: 0;">→ streamguard_threats.quarantine</p>
                <div class="tooltip" style="border: 1px solid #4ECDC4;">
                    <p style="color: #4ECDC4; font-weight: 700; font-size: 0.75rem; margin: 0 0 0.5rem 0;">WHY THIS RESOURCE?</p>
                    <p style="color: #C9D1D9; font-size: 0.75rem; margin: 0; line-height: 1.4;">Streams quarantined transactions to BigQuery for compliance audit, enabling forensic analysis and regulatory reporting requirements.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Flow explanation
        st.markdown("""
        <p style="text-align: center; color: #8B949E; font-size: 0.9rem; margin: 1.5rem 0 2rem 0;">
            All of Betty's future transactions flow through this isolated pipeline
        </p>
        """, unsafe_allow_html=True)
        
        # Privacy Note
        st.markdown("""
        <div style="background: rgba(255, 193, 7, 0.1); border-left: 4px solid #FFC107; padding: 1rem; border-radius: 4px; margin-top: 2rem;">
            <p style="color: #FFC107; font-weight: 600; margin: 0 0 0.5rem 0;">⚠️ Demo Mode</p>
            <p style="color: #8B949E; font-size: 0.85rem; margin: 0;">
                Customer names like "betty-senior" and resource names like <code>fraud-quarantine-betty-senior</code> 
                are used for explanatory purposes only. In production, all identifiers are anonymized 
                (e.g., <code>user_a1b2c3</code>, <code>quarantine-7f8e9d</code>).
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div style="height: 30px;"></div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Next: Summary →", type="primary", use_container_width=True):
                st.session_state.current_step = 6
                st.rerun()
