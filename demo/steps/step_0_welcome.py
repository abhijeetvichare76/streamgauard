import streamlit as st

def render():
    narrative_html = """
<div id="aegis-storyboard" style="opacity: 1;">
<!-- Scene 1: Hero & Branding -->
<section class="scroll-fold" id="scene-1" style="min-height: 95vh;">
<div style="text-align: center; max-width: 1000px; margin: 0 auto;">
<div class="reveal-item branding-logo" style="display: flex; align-items: center; justify-content: center; gap: 30px; margin-bottom: 4rem;">
<div class="logo-line logo-line-left"></div>
<span style="font-size: 2.8rem; font-weight: 900; letter-spacing: 22px; color: #4ECDC4; text-transform: uppercase; margin-right: -22px; filter: drop-shadow(0 0 15px rgba(78,205,196,0.3));">STREAMGUARD</span>
<div class="logo-line logo-line-right"></div>
</div>
<h1 class="reveal-item gradient-hero" style="font-size: 4.8rem; line-height: 1.05; margin-bottom: 2rem; letter-spacing: -3px;">Real-Time Fraud Detection.<br>Real-Time Actions.</h1>
<p class="reveal-item subtitle" style="font-size: 1.6rem; color: #8B949E; font-weight: 400; letter-spacing: 1px;">When Every Transaction Could Be Someone's Life Savings</p>
</div>
<div class="scroll-indicator" style="margin-top: 5rem;">
<div class="scroll-text">Scroll to Begin</div>
<span></span>
<span></span>
</div>
</section>

<!-- Scene 2: Betty's Story -->
<section class="scroll-fold" id="scene-2">
<div style="max-width: 900px; margin: 0 auto; width: 100%;">
<p class="section-label" style="text-align: center;">3:47 PM — A Phone Rings</p>
<div style="display: flex; align-items: flex-start; margin-bottom: 5rem;">
<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; width: 120px; flex-shrink: 0;">
<div class="voice-wave">
<div style="width: 3px; background: #8B949E; border-radius: 2px; animation: wave-pulse 1.2s infinite ease-in-out; animation-duration: 0.8s;"></div>
<div style="width: 3px; background: #8B949E; border-radius: 2px; animation: wave-pulse 1.2s infinite ease-in-out; animation-duration: 1.2s; height: 30px;"></div>
<div style="width: 3px; background: #8B949E; border-radius: 2px; animation: wave-pulse 1.2s infinite ease-in-out; animation-duration: 0.6s; height: 15px;"></div>
<div style="width: 3px; background: #8B949E; border-radius: 2px; animation: wave-pulse 1.2s infinite ease-in-out; animation-duration: 1.0s; height: 25px;"></div>
<div style="width: 3px; background: #8B949E; border-radius: 2px; animation: wave-pulse 1.2s infinite ease-in-out; animation-duration: 0.9s;"></div>
</div>
<p style="font-size: 0.7rem; color: #8B949E; margin-top: 15px; text-transform: uppercase; letter-spacing: 3px; font-weight: 700;">VOICE CALL</p>
</div>
<div class="sms-bubble reveal-item">
<p style="color: #FAFAFA; font-size: 1.35rem; line-height: 1.6; margin: 0; font-weight: 300;">
"Grandma, it's me! I'm in trouble and need your help urgently. My car broke down and I need to pay the mechanic right away. Can you send $5,000 to this account for the repairs?"
</p>
</div>
</div>
<div style="text-align: center; margin-bottom: 4rem;">
<p class="reveal-item" style="font-size: 1.6rem; color: #FAFAFA; margin-bottom: 0.5rem; font-weight: 600;">Betty, 75, recognized her grandson's voice.</p>
<p class="reveal-item" style="font-size: 1.25rem; color: #8B949E; font-weight: 400;">It was AI-generated. But she didn't know that.</p>
</div>
<div style="max-width: 550px; margin: 0 auto 5rem auto; background: rgba(255,255,255,0.02); padding: 3rem; border-radius: 24px; border: 1px solid rgba(255,255,255,0.05); box-shadow: 0 20px 50px rgba(0,0,0,0.3);">
<div class="reveal-item" style="margin-bottom: 1.5rem; font-size: 1.2rem; display: flex; align-items: center;"><span class="checkmark-green" style="font-size: 1.4rem;">✓</span> <span>She logged in with her own credentials</span></div>
<div class="reveal-item" style="margin-bottom: 1.5rem; font-size: 1.2rem; display: flex; align-items: center;"><span class="checkmark-green" style="font-size: 1.4rem;">✓</span> <span>From her own phone, sitting at home</span></div>
<div class="reveal-item" style="margin-bottom: 1.5rem; font-size: 1.2rem; display: flex; align-items: center;"><span class="checkmark-green" style="font-size: 1.4rem;">✓</span> <span>She typed the amount herself: <b style="color:#FAFAFA; font-size: 1.4rem; margin-left:10px;">$5,000</b></span></div>
<div class="reveal-item" style="display: flex; align-items: center; font-size: 1.2rem;"><span class="checkmark-green" style="font-size: 1.4rem;">✓</span> <span>She clicked "Confirm Transfer"</span></div>
</div>
<div style="text-align: center;">
<p class="reveal-item" style="font-size: 1.4rem; color: #8B949E; margin-bottom: 1.5rem; font-weight: 300;">Her bank's fraud system saw nothing wrong.</p>
<p class="reveal-item punch-red shake-anim" style="font-size: 2.2rem; filter: drop-shadow(0 0 20px rgba(255,107,107,0.4));">By the time she realized, the money was gone.</p>
</div>
</div>
</section>

<!-- Scene 3: APP Fraud Analysis (Revised Layout) -->
<section class="scroll-fold" id="scene-3">
<div style="max-width: 1000px; margin: 0 auto; text-align: center; width: 100%;">
<h2 class="reveal-item" style="color: #4ECDC4; font-size: 2.8rem; margin-bottom: 4rem; font-weight: 800;">What is APP Fraud?</h2>

<div class="acronym-box reveal-item" style="justify-content: center; margin-bottom: 5rem; padding: 3rem; width: 100%;">
<div style="display: flex; flex-direction: column; align-items: center; gap: 10px; min-width: 180px;">
<span class="acronym-letter" style="font-size: 5rem; line-height: 1;">A</span>
<span class="acronym-word" style="font-size: 1.2rem; color: #8B949E; font-weight: 600; font-family: 'JetBrains Mono'; letter-spacing: 1px;">AUTHORIZED</span>
</div>
<div style="display: flex; flex-direction: column; align-items: center; gap: 10px; min-width: 120px;">
<span class="acronym-letter" style="font-size: 5rem; line-height: 1;">P</span>
<span class="acronym-word" style="font-size: 1.2rem; color: #8B949E; font-weight: 600; font-family: 'JetBrains Mono'; letter-spacing: 1px;">PUSH</span>
</div>
<div style="display: flex; flex-direction: column; align-items: center; gap: 10px; min-width: 180px;">
<span class="acronym-letter" style="font-size: 5rem; line-height: 1;">P</span>
<span class="acronym-word" style="font-size: 1.2rem; color: #8B949E; font-weight: 600; font-family: 'JetBrains Mono'; letter-spacing: 1px;">PAYMENT</span>
</div>
</div>

<p class="reveal-item" style="font-size: 1.4rem; color: #FAFAFA; max-width: 800px; margin: 0 auto 4rem auto; line-height: 1.6;">
Unlike stolen cards or hacked accounts, <b style="color: #4ECDC4;">APP fraud is unique</b> because the victim plays an active role.
</p>

<div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 3rem; margin-bottom: 6rem;">
<div class="custom-card reveal-item" style="margin:0 !important; border-top: 4px solid #4ECDC4;">
<p style="font-size: 3rem; margin-bottom: 1.5rem; opacity: 0.3; font-weight: 800;">1</p>
<p style="font-size: 1.15rem; color: #FAFAFA; line-height: 1.5;">The victim <b style="color:#4ECDC4">authorizes</b> the payment themselves.</p>
</div>
<div class="custom-card reveal-item" style="margin:0 !important; border-top: 4px solid #58A6FF;">
<p style="font-size: 3rem; margin-bottom: 1.5rem; opacity: 0.3; font-weight: 800;">2</p>
<p style="font-size: 1.15rem; color: #FAFAFA; line-height: 1.5;">The bank sees a <b style="color:#58A6FF">legitimate</b> login session.</p>
</div>
<div class="custom-card reveal-item" style="margin:0 !important; border-top: 4px solid #FF6B6B;">
<p style="font-size: 3rem; margin-bottom: 1.5rem; opacity: 0.3; font-weight: 800;">3</p>
<p style="font-size: 1.15rem; color: #FAFAFA; line-height: 1.5;">The money leaves <b style="color:#FF6B6B">instantly</b> and irreversibly.</p>
</div>
</div>

<div class="reveal-item" style="margin-bottom: 2rem;">
<p style="font-size: 1.5rem; color: #8B949E; font-weight: 300;">While traditional systems check the <span class="strikethrough">SYSTEM</span>...</p>
<p style="font-size: 2.2rem; color: #FAFAFA; font-weight: 700; margin-top: 1rem;">StreamGuard checks the <span class="human-highlight">HUMAN CONTEXT</span>.</p>
</div>
</div>
</section>

<!-- Scene 4: The Detection Gap -->
<section class="scroll-fold" id="scene-4">
<div style="max-width: 900px; margin: 0 auto; width: 100%;">
<p class="section-label" style="text-align: center;">The Detection Gap</p>
<h2 class="reveal-item" style="text-align: center; color: #FAFAFA; font-size: 2.4rem; margin-bottom: 3rem;">Why Banks Can't Stop It (Yet)</h2>

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 4rem; align-items: center;">
<div class="reveal-item" style="background: rgba(255,255,255,0.03); padding: 2.5rem; border-radius: 16px; border: 1px solid rgba(255,255,255,0.1);">
<h3 style="color: #4ECDC4; margin-bottom: 1.5rem; font-size: 1.4rem;">Standard Security Checks</h3>
<div style="display: flex; justify-content: space-between; margin-bottom: 1rem; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 0.5rem;">
<span style="color: #c9d1d9;">Valid Password?</span>
<span style="color: #3FB950;">YES ✓</span>
</div>
<div style="display: flex; justify-content: space-between; margin-bottom: 1rem; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 0.5rem;">
<span style="color: #c9d1d9;">Correct Device?</span>
<span style="color: #3FB950;">YES ✓</span>
</div>
<div style="display: flex; justify-content: space-between; margin-bottom: 1rem; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 0.5rem;">
<span style="color: #c9d1d9;">Known Location?</span>
<span style="color: #3FB950;">YES ✓</span>
</div>
<div style="display: flex; justify-content: space-between; margin-bottom: 1.5rem;">
<span style="color: #c9d1d9;">2FA Passed?</span>
<span style="color: #3FB950;">YES ✓</span>
</div>
<div style="text-align: center; background: rgba(63, 185, 80, 0.2); padding: 1rem; border-radius: 8px; color: #3FB950; font-weight: 800; letter-spacing: 1px;">
APPROVED ✅
</div>
</div>

<div class="reveal-item">
<p style="font-size: 1.6rem; font-weight: 700; color: #FAFAFA; margin-bottom: 2rem; line-height: 1.4;">
The system is working perfectly.<br>
<span style="color: #FF6B6B;">But the Human is Compromised.</span>
</p>
<div style="display: flex; flex-direction: column; gap: 1.5rem;">
<div style="display: flex; gap: 15px; align-items: start;">
<span class="orange-pulse" style="font-size: 1.5rem;">?</span>
<span style="color: #8B949E; font-size: 1.1rem; line-height: 1.4;">Is someone coaching them on a call right now?</span>
</div>
<div style="display: flex; gap: 15px; align-items: start;">
<span class="orange-pulse" style="font-size: 1.5rem;">?</span>
<span style="color: #8B949E; font-size: 1.1rem; line-height: 1.4;">Is this new recipient an account created 2 hours ago?</span>
</div>
<div style="display: flex; gap: 15px; align-items: start;">
<span class="orange-pulse" style="font-size: 1.5rem;">?</span>
<span style="color: #8B949E; font-size: 1.1rem; line-height: 1.4;">Did they rush through the screens in 10 seconds?</span>
</div>
</div>
</div>
</div>
</div>
</section>

<!-- Scene 5: The Scale -->
<section class="scroll-fold" id="scene-5">
<div style="max-width: 1000px; margin: 0 auto; width: 100%;">
<h2 class="reveal-item" style="text-align: center; color: #FAFAFA; font-size: 3rem; margin-bottom: 5rem;">The Scale of the Problem</h2>

<div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 2rem; margin-bottom: 4rem;">
<div class="metric-box reveal-item">
<p class="metric-value">$12.5B</p>
<p class="metric-label">US Fraud Losses (2024 Est.)</p>
<p style="margin:0; font-size: 0.7rem; opacity: 0.5;">Source: FTC Data</p>
</div>
<div class="metric-box reveal-item">
<p class="metric-value">80%</p>
<p class="metric-label">Of victims on a call with scammer</p>
<p style="margin:0; font-size: 0.7rem; opacity: 0.5;">Source: FCC Reports</p>
</div>
<div class="metric-box reveal-item">
<p class="metric-value">77%</p>
<p class="metric-label">Success rate of AI Voice Scams</p>
<p style="margin:0; font-size: 0.7rem; opacity: 0.5;">Source: McAfee</p>
</div>
</div>

<p class="reveal-item" style="text-align: center; font-size: 1.2rem; color: #8B949E; font-style: italic;">
"And these are just the reported cases. Shame keeps many victims silent."
</p>
</div>
</section>

<!-- Scene 6: What's Needed -->
<section class="scroll-fold" id="scene-6">
<div style="max-width: 900px; margin: 0 auto; width: 100%; text-align: center;">
<p class="section-label">The Solution</p>
<h2 class="reveal-item" style="font-size: 3rem; background: linear-gradient(135deg, #FFF 0%, #8B949E 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 3rem;">We need a system that can:</h2>

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; text-align: left;">
<div class="custom-card reveal-item" style="margin: 0 !important;">
<div style="font-size: 2rem; margin-bottom: 1rem;">⚡ React in Real-Time</div>
<p style="color: #8B949E;">Decisions in milliseconds, not batch analysis hours later.</p>
</div>
<div class="custom-card reveal-item" style="margin: 0 !important;">
<div style="font-size: 2rem; margin-bottom: 1rem;">🔍 Gather Deep Context</div>
<p style="color: #8B949E;">Synthesize profile history, graph relationships, and live device signals.</p>
</div>
<div class="custom-card reveal-item" style="margin: 0 !important;">
<div style="font-size: 2rem; margin-bottom: 1rem;">🧠 Reason Like a Human</div>
<p style="color: #8B949E;">Apply nuanced judgment to gray areas, not just binary rules.</p>
</div>
<div class="custom-card reveal-item" style="margin: 0 !important; border-color: #4ECDC4 !important; background: rgba(78, 205, 196, 0.05) !important;">
<div style="font-size: 2rem; margin-bottom: 1rem; color: #4ECDC4;">🛡️ Respond Autonomously</div>
<p style="color: #FAFAFA;">Create infrastructure, route traffic, and protect funds without human delay.</p>
</div>
</div>
</div>
</section>

<!-- Scene 7: The StreamGuard Swarm -->
<section class="scroll-fold" id="scene-7">
<div style="max-width: 1000px; margin: 0 auto; width: 100%;">
<h2 class="reveal-item" style="text-align: center; color: #4ECDC4; font-size: 3rem; margin-bottom: 1rem;">The StreamGuard Agent Swarm</h2>
<p class="reveal-item" style="text-align: center; color: #8B949E; margin-bottom: 4rem;">Powered by Google Agent Development Kit (ADK)</p>

<div style="display: flex; gap: 2rem; align-items: stretch; justify-content: center;">
<div class="reveal-item" style="flex: 1; background: rgba(255,255,255,0.03); padding: 2rem; border-radius: 12px; border-top: 3px solid #FF6B6B;">
<div style="font-size: 3rem; margin-bottom: 1rem;">🕵️</div>
<h3 style="color: #FF6B6B; margin-bottom: 1rem;">DETECTIVE</h3>
<p style="font-size: 0.9rem; color: #c9d1d9;">Investigates context from multiple sources:</p>
<ul style="font-size: 0.85rem; color: #8B949E; padding-left: 1.2rem; line-height: 1.6;">
<li>Customer Profiles</li>
<li>Beneficiary Graph</li>
<li>Live Session Data</li>
</ul>
</div>

<div class="swarm-arrow reveal-item"></div>

<div class="reveal-item" style="flex: 1; background: rgba(255,255,255,0.03); padding: 2rem; border-radius: 12px; border-top: 3px solid #D29922;">
<div style="font-size: 3rem; margin-bottom: 1rem;">⚖️</div>
<h3 style="color: #D29922; margin-bottom: 1rem;">JUDGE</h3>
<p style="font-size: 0.9rem; color: #c9d1d9;">Applies bank policies priority order:</p>
<ul style="font-size: 0.85rem; color: #8B949E; padding-left: 1.2rem; line-height: 1.6;">
<li>Active Call + Elderly = BLOCK</li>
<li>New Beneficiary = ESCALATE</li>
<li>VIP Customer = REVIEW</li>
</ul>
</div>

<div class="swarm-arrow reveal-item"></div>

<div class="reveal-item" style="flex: 1; background: rgba(255,255,255,0.03); padding: 2rem; border-radius: 12px; border-top: 3px solid #4ECDC4;">
<div style="font-size: 3rem; margin-bottom: 1rem;">🛡️</div>
<h3 style="color: #4ECDC4; margin-bottom: 1rem;">ENFORCER</h3>
<p style="font-size: 0.9rem; color: #c9d1d9;">Creates real infrastructure instantly:</p>
<ul style="font-size: 0.85rem; color: #8B949E; padding-left: 1.2rem; line-height: 1.6;">
<li>Creates Quarantine Topic</li>
<li>Deploys Flink Route</li>
<li>Alerts Security Team</li>
</ul>
</div>
</div>
</div>
</section>

"""
    # Render first part of narrative
    st.markdown(narrative_html, unsafe_allow_html=True)

    # Scene 8: System Architecture (Dynamic Code-Based Diagram)
    st.markdown('<section class="scroll-fold" id="scene-8"><div style="max-width: 1200px; margin: 0 auto; width: 100%;">', unsafe_allow_html=True)
    st.markdown('<h2 class="reveal-item" style="text-align: center; color: #4ECDC4; font-size: 2.8rem; margin-bottom: 4rem;">System Architecture</h2>', unsafe_allow_html=True)
    
    try:
        import os
        if os.path.exists("demo/assets/aegis_architecture.png"):
            # Use columns to center the image effectively
            col_spacer1, col_img, col_spacer2 = st.columns([1, 8, 1])
            with col_img:
                st.image("demo/assets/aegis_architecture.png", width="stretch")
                st.markdown('<p style="text-align: center; color: #8B949E; margin-top: 1rem; font-style: italic;">Generated via Diagrams as Code</p>', unsafe_allow_html=True)
        else:
            st.warning("Architecture diagram not found at 'demo/assets/aegis_architecture.png'. Please generate it.")
    except Exception as e:
        st.error(f"Error displaying architecture: {e}")

    st.markdown('</div></section>', unsafe_allow_html=True)

    # Start second part of narrative for Scene 9
    narrative_html_2 = """

<!-- Scene 9: Call to Action -->
<section class="scroll-fold" id="scene-9" style="min-height: 80vh;">
<div style="text-align: center; max-width: 800px; margin: 0 auto;">
<div class="reveal-item branding-logo" style="display: flex; align-items: center; justify-content: center; gap: 20px; margin-bottom: 3.5rem;">
<div class="logo-line logo-line-left" style="width: 60px;"></div>
<span style="font-size: 2rem; font-weight: 900; letter-spacing: 12px; color: #4ECDC4; text-transform: uppercase; margin-right: -12px;">STREAMGUARD</span>
<div class="logo-line logo-line-right" style="width: 60px;"></div>
</div>
<h2 class="reveal-item" style="color: #FAFAFA; font-size: 3.2rem; line-height: 1.2; margin-bottom: 2rem; font-weight: 800;">Protect Your Customers.<br>Preserve Their Trust.</h2>
<p class="reveal-item" style="color: #8B949E; font-size: 1.4rem; margin-bottom: 5rem; font-weight: 300;">
Step inside the dashboard to see how the StreamGuard swarm identifies the invisible threads of fraud.
</p>

<div class="reveal-item" style="display: flex; justify-content: center;">
<div id="cta-button-placeholder"></div>
</div>
</div>
</section>
</div>

<style>
/* Logo Line Component */
.logo-line {
height: 2px;
width: 100px;
}
.logo-line-left {
background: linear-gradient(90deg, transparent, #4ECDC4);
}
.logo-line-right {
background: linear-gradient(90deg, #4ECDC4, transparent);
}
</style>
    """
    # Render second narrative block
    st.markdown(narrative_html_2, unsafe_allow_html=True)

    # CTA Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True) # Spacer
        if st.button("🚀 Start StreamGuard Fraud Detection Tutorial", type="primary", use_container_width=True):
            st.session_state.current_step = 1
            st.rerun()

    # Copyright text below button
    st.markdown("""
    <p style="text-align: center; color: #4B5563; font-size: 0.95rem; margin-top: 3rem; letter-spacing: 2px; font-weight: 500;">
        © 2024 STREAMGUARD • BUILT FOR INNOVATION
    </p>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
