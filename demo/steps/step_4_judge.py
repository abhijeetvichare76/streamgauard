import streamlit as st

def render():
    st.markdown('<p class="section-label">Step 4 of 6</p>', unsafe_allow_html=True)
    st.title("Judge Agent Applies Policy")
    st.markdown("<p style='color: #8B949E; font-size: 1.1rem; margin-bottom: 2rem;'>The Judge Agent evaluates the Detective's findings against institutional compliance policies. Every decision is explainable and backed by evidence.</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("""
        <div class="custom-card" style="height: 100%;">
            <h4 style="color: #4ECDC4; margin-top:0; margin-bottom: 1.5rem;">Policy Compliance Matrix</h4>
            <table style="width:100%; color: #8B949E; border-collapse: collapse; font-size: 0.95rem;">
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                    <th style="text-align:left; padding: 12px; color: #FAFAFA;">Policy ID</th>
                    <th style="text-align:right; padding: 12px; color: #FAFAFA;">Status</th>
                </tr>
                <tr>
                    <td style="padding: 12px; color: #FAFAFA; font-weight: 600;">P-101: Active Voice Call Override</td>
                    <td style="text-align:right; padding: 12px; color: #3FB950; font-weight: 800;">TRIGGERED ✅</td>
                </tr>
                <tr style="opacity: 0.5;">
                    <td style="padding: 12px;">P-102: Repeat Offender Check</td>
                    <td style="text-align:right; padding: 12px;">NOT MET ○</td>
                </tr>
                <tr style="opacity: 0.5;">
                    <td style="padding: 12px;">P-103: New Account Escalation</td>
                    <td style="text-align:right; padding: 12px;">NOT MET ○</td>
                </tr>
                <tr>
                    <td style="padding: 12px; color: #FAFAFA; font-weight: 600;">P-104: High Velocity Anomaly</td>
                    <td style="text-align:right; padding: 12px; color: #3FB950; font-weight: 800;">TRIGGERED ✅</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="custom-card" style="border-left: 6px solid #F85149; height: 100%;">
            <h4 style="color: #F85149; margin-top: 0; margin-bottom: 1.5rem;">The Verdict</h4>
            <div style="margin-bottom: 1.5rem; background: rgba(248, 81, 73, 0.1); padding: 1rem; border-radius: 8px;">
                <label style="color: #8B949E; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; font-weight:700;">FINAL DECISION</label>
                <div style="font-size: 2rem; font-weight: 900; color: #F85149;">DENY & ISOLATE</div>
            </div>
            <div style="margin-bottom: 1.5rem;">
                <label style="color: #8B949E; font-size: 0.75rem; text-transform: uppercase;">Confidence</label>
                <div style="font-size: 1.4rem; font-weight: 700; color: #FAFAFA;">98.4%</div>
            </div>
            <div>
                <label style="color: #8B949E; font-size: 0.75rem; text-transform: uppercase;">Judge's Notes</label>
                <div style="font-size: 0.95rem; font-style: italic; color: #FAFAFA; line-height: 1.6; margin-top: 0.5rem;">
                    "The combination of a 100x value increase, new beneficiary target, and real-time voice-call telemetry confirms coaching fraud. Action: Block transaction and trigger Enforcer for resource isolation."
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    if st.button("Next: Enforcer Execution →"):
        st.session_state.current_step = 5
        st.rerun()
