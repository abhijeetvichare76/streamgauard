import streamlit as st

def load_custom_css():
    st.markdown("""
        <style>
            /* Import Inter and JetBrains Mono fonts */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

            /* Global Font Override */
            html, body, [class*="css"] {
                font-family: 'Inter', sans-serif !important;
            }

            /* Glassmorphism Card styling - MOORE VISIBLE */
            .custom-card {
                background: rgba(255, 255, 255, 0.03) !important;
                backdrop-filter: blur(16px) !important;
                -webkit-backdrop-filter: blur(16px) !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                border-radius: 20px !important;
                padding: 2.5rem !important;
                margin: 2rem 0 !important;
                box-shadow: 0 10px 40px -10px rgba(0, 0, 0, 0.5) !important;
            }

            /* Metric Box - HIGH CONTRAST */
            .metric-box {
                background: rgba(255, 255, 255, 0.05) !important;
                backdrop-filter: blur(10px) !important;
                border: 1px solid rgba(78, 205, 196, 0.2) !important;
                border-radius: 16px !important;
                padding: 1.5rem !important;
                text-align: center !important;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
                transition: all 0.3s ease !important;
                display: flex !important;
                flex-direction: column !important;
                justify-content: center !important;
            }
            .metric-box:hover {
                transform: translateY(-8px) scale(1.02) !important;
                border-color: #4ECDC4 !important;
                background: rgba(78, 205, 196, 0.1) !important;
                box-shadow: 0 12px 30px rgba(78, 205, 196, 0.2) !important;
            }

            .metric-value {
                font-size: 2.8rem !important;
                font-weight: 800 !important;
                color: #4ECDC4 !important;
                margin-bottom: 0.25rem !important;
                line-height: 1 !important;
            }

            .metric-label {
                font-size: 0.8rem !important;
                color: #8B949E !important;
                text-transform: uppercase !important;
                letter-spacing: 2px !important;
                font-weight: 600 !important;
            }

            /* Hero Styling - BIGGER & BRIGHTER */
            .gradient-hero {
                background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 50%, #58A6FF 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-size: 5rem;
                font-weight: 900;
                margin-bottom: 0.5rem;
                letter-spacing: -3px;
                filter: drop-shadow(0 0 30px rgba(78, 205, 196, 0.2));
            }
            
            .subtitle {
                font-size: 1.8rem;
                color: #FAFAFA;
                margin-bottom: 2.5rem;
                font-weight: 600;
                opacity: 0.8;
                letter-spacing: -0.5px;
            }

            /* Log container - Terminal vibe */
            .log-container {
                background: #0D1117 !important;
                border: 1px solid #30363d !important;
                border-radius: 15px !important;
                padding: 1.5rem !important;
                font-family: 'JetBrains Mono', monospace !important;
                font-size: 0.95rem !important;
                color: #c9d1d9 !important;
                line-height: 1.7 !important;
                box-shadow: inset 0 0 20px rgba(0,0,0,0.6) !important;
            }

            /* Buttons - Premium Gradient */
            .stButton > button {
                border-radius: 12px !important;
                padding: 1rem 3rem !important;
                font-weight: 800 !important;
                text-transform: uppercase !important;
                letter-spacing: 1.5px !important;
                background: linear-gradient(135deg, #4ECDC4 0%, #3FB950 100%) !important;
                color: #0E1117 !important;
                border: none !important;
                box-shadow: 0 10px 30px rgba(63, 185, 80, 0.2) !important;
            }
            .stButton > button:hover {
                background: linear-gradient(135deg, #58A6FF 0%, #4ECDC4 100%) !important;
                transform: translateY(-3px) !important;
                box-shadow: 0 15px 40px rgba(88, 166, 255, 0.3) !important;
            }
            
            /* Section Label - Accent Color */
            .section-label {
                color: #4ECDC4 !important;
                font-weight: 800 !important;
                text-transform: uppercase !important;
                letter-spacing: 4px !important;
                font-size: 1.1rem !important;
                margin-bottom: 2rem !important;
                opacity: 0.8;
            }

            /* Scrollytelling Folds */
            .scroll-fold {
                position: relative;
                min-height: 90vh !important;
                display: flex !important;
                flex-direction: column !important;
                justify-content: center !important;
                align-items: center !important;
                padding: 6rem 2rem !important;
                opacity: 1;
            }

            /* Scroll Indicator */
            .scroll-indicator {
                position: absolute;
                bottom: 15%;
                left: 50%;
                transform: translateX(-50%);
                text-align: center;
                animation: bounce 2s infinite;
                cursor: pointer;
            }

            .scroll-indicator span {
                display: block;
                width: 20px;
                height: 20px;
                border-bottom: 2px solid #8B949E;
                border-right: 2px solid #8B949E;
                transform: rotate(45deg);
                margin: -10px auto;
            }

            .scroll-text {
                font-family: 'Inter', sans-serif;
                font-size: 0.7rem;
                color: #4ECDC4;
                text-transform: uppercase;
                letter-spacing: 3px;
                margin-bottom: 15px;
            }

            @keyframes bounce {
                0%, 20%, 50%, 80%, 100% {transform: translateX(-50%) translateY(0);}
                40% {transform: translateX(-50%) translateY(-10px);}
                60% {transform: translateX(-50%) translateY(-5px);}
            }

            /* Voice Wave Animation */
            .voice-wave {
                display: flex;
                align-items: center;
                gap: 3px;
                height: 40px;
            }
            .voice-line {
                width: 3px;
                background: #8B949E;
                border-radius: 2px;
                animation: wave-pulse 1.2s infinite ease-in-out;
            }
            @keyframes wave-pulse {
                0%, 100% { height: 5px; opacity: 0.3; }
                50% { height: 35px; opacity: 1; }
            }

            /* Typewriter Bubble */
            .sms-bubble {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                padding: 1.5rem 2rem;
                max-width: 600px;
                position: relative;
                margin-left: 1rem;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }

            /* staggered reveals - ROBUST CSS-ONLY VERSION */
            .reveal-item {
                opacity: 1; /* Fallback: Always visible */
                transform: none;
            }

            /* Modern Scroll Animations (No JS required) */
            @supports (animation-timeline: view()) {
                .reveal-item {
                    animation: auto-reveal linear both;
                    animation-timeline: view();
                    animation-range: entry 5% cover 30%;
                }
                @keyframes auto-reveal {
                    from { opacity: 0; transform: translateY(50px); filter: blur(4px); }
                    to { opacity: 1; transform: translateY(0); filter: blur(0); }
                }
                
                /* Manual stagger for hero items by delaying the start range slightly */
                #scene-1 .reveal-item:nth-child(1) { animation-range: entry 0% contain 20%; }
                #scene-1 .reveal-item:nth-child(2) { animation-range: entry 5% contain 25%; }
                #scene-1 .reveal-item:nth-child(3) { animation-range: entry 10% contain 30%; }
            }
            
            /* Fallback for staggered delays if timeline not supported (optional, requires JS to trigger class, but we are skipping JS reliant logic) */
            .reveal-item:nth-child(2) { transition-delay: 0.3s; }
            .reveal-item:nth-child(3) { transition-delay: 0.5s; }
            .reveal-item:nth-child(4) { transition-delay: 0.7s; }
            .reveal-item:nth-child(5) { transition-delay: 0.9s; }

            .checkmark-green {
                color: #3FB950;
                font-weight: 800;
                margin-right: 10px;
            }

            .punch-red {
                color: #FF6B6B !important;
                font-weight: 800;
            }

            .shake-anim {
                animation: subtle-shake 0.5s ease-in-out;
            }
            @keyframes subtle-shake {
                0%, 100% { transform: translateX(0); }
                25% { transform: translateX(-2px); }
                75% { transform: translateX(2px); }
            }
            /* APP Acronym Effect */
            .acronym-box {
                background: rgba(78, 205, 196, 0.05);
                border: 1px solid #4ECDC4;
                border-radius: 12px;
                padding: 1.5rem;
                display: inline-flex;
                gap: 2rem;
                align-items: center;
                margin-bottom: 2rem;
            }
            .acronym-letter {
                font-size: 2.5rem;
                font-weight: 900;
                color: #4ECDC4;
            }
            .acronym-word {
                font-size: 1.5rem;
                color: #FAFAFA;
                opacity: 1;
            }
            .scroll-fold.in-view .acronym-word {
                animation: reveal-in 0.5s forwards;
            }

            /* Timeline Animation */
            .timeline-wrapper {
                position: relative;
                padding: 2rem 0;
                margin: 3rem 0;
                display: flex;
                justify-content: space-between;
                max-width: 600px;
                margin-left: auto;
                margin-right: auto;
            }
            .timeline-track {
                position: absolute;
                top: 50%;
                left: 0;
                width: 0;
                height: 4px;
                background: linear-gradient(90deg, #4ECDC4, #FF6B6B);
                transform: translateY(-50%);
                z-index: 1;
            }
            .scroll-fold.in-view .timeline-track {
                animation: draw-line 3s forwards ease-in-out;
                animation-delay: 2s; /* reduced delay since fold triggers it */
            }
            @keyframes draw-line {
                to { width: 100%; }
            }

            .timeline-step {
                width: 50px;
                height: 50px;
                background: #1E2530;
                border: 2px solid #2D3748;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 800;
                position: relative;
                z-index: 2;
                transition: all 0.5s ease;
            }
            .step-active {
                border-color: #4ECDC4 !important;
                box-shadow: 0 0 20px rgba(78, 205, 196, 0.4) !important;
                background: #4ECDC4 !important;
                color: #0E1117 !important;
            }

            .timeline-label {
                position: absolute;
                bottom: -35px;
                width: 100px;
                text-align: center;
                font-size: 0.8rem;
                color: #8B949E;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
            }

            /* Detection Gap Specials */
            .strikethrough {
                text-decoration: line-through;
                opacity: 0.5;
            }
            .human-highlight {
                color: #FCD34D !important;
                text-shadow: 0 0 10px rgba(252, 211, 77, 0.4);
                font-weight: 800;
            }
            .orange-pulse {
                color: #FCD34D;
                display: inline-block;
                animation: orange-glow 2s infinite;
            }
            @keyframes orange-glow {
                0%, 100% { transform: scale(1); opacity: 0.8; }
                50% { transform: scale(1.2); opacity: 1; text-shadow: 0 0 15px #FCD34D; }
            }

            /* Architecture Diagram */
            .arch-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 1.5rem;
                margin: 4rem 0;
            }
            .arch-box {
                width: 100%;
                max-width: 700px;
                padding: 1.5rem;
                border-radius: 12px;
                border: 1px solid rgba(255,255,255,0.1);
                background: rgba(255,255,255,0.02);
                text-align: center;
                position: relative;
            }
            .arch-box h4 {
                margin: 0 0 0.5rem 0;
                font-size: 0.9rem;
                letter-spacing: 2px;
                text-transform: uppercase;
            }
            .arch-box p {
                margin: 0;
                font-size: 0.8rem;
                color: #8B949E;
            }
            .arch-arrow {
                height: 30px;
                width: 2px;
                background: linear-gradient(to bottom, #4ECDC4, transparent);
                animation: flow-down 2s infinite linear;
            }
            @keyframes flow-down {
                0% { background-position: 0 -30px; opacity: 0; }
                50% { opacity: 1; }
                100% { background-position: 0 30px; opacity: 0; }
            }
            
            /* Swarm Arrow (horizontal flow) */
            .swarm-arrow {
                width: 60px;
                height: 3px;
                position: relative;
                background: linear-gradient(to right, transparent, #4ECDC4, transparent);
                animation: flow-right 2s infinite linear;
            }
            .swarm-arrow::after {
                content: '→';
                position: absolute;
                right: -10px;
                top: 50%;
                transform: translateY(-50%);
                color: #4ECDC4;
                font-size: 1.5rem;
                animation: pulse-arrow 2s infinite;
            }
            @keyframes flow-right {
                0% { opacity: 0.3; }
                50% { opacity: 1; }
                100% { opacity: 0.3; }
            }
            @keyframes pulse-arrow {
                0%, 100% { opacity: 0.5; transform: translateY(-50%) translateX(0); }
                50% { opacity: 1; transform: translateY(-50%) translateX(5px); }
            }
            .arch-legend {
                display: flex;
                justify-content: center;
                gap: 2rem;
                margin-top: 2rem;
                font-size: 0.7rem;
                color: #8B949E;
            }
            .legend-item {
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            .legend-dot {
                width: 8px;
                height: 8px;
                border-radius: 50%;
            }
        </style>
    """,unsafe_allow_html=True)
