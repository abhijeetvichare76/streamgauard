import streamlit as st
from styles.css import load_custom_css
from steps import STEP_REGISTRY

def main():
    # Page configuration
    st.set_page_config(
        page_title="StreamGuard",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Load custom CSS
    load_custom_css()

    # Initialize session state
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0
    if 'app_mode' not in st.session_state:
        st.session_state.app_mode = "Tutorial"

    # Sidebar navigation

    # Header navigation (text-based, no buttons/boxes)
    tutorial_active = st.session_state.app_mode == "Tutorial"
    playground_active = st.session_state.app_mode == "Playground"

    # Start navigation container
    st.markdown('<div class="header-nav-container">', unsafe_allow_html=True)

    # Custom CSS to style ONLY navigation buttons
    st.markdown("""
    <style>
    /* Target specifically the navigation buttons using the marker class above them */
    [data-testid="stVerticalBlock"] > div:has(.header-nav-container) + div + div button {
        background: transparent !important;
        border: none !important;
        padding: 0 0.25rem !important;
        box-shadow: none !important;
        color: #8B949E !important;
        font-weight: 400 !important;
        font-size: 1rem !important;
        min-height: auto !important;
        height: auto !important;
        width: auto !important;
        margin-top: 0px !important;
    }
    [data-testid="stVerticalBlock"] > div:has(.header-nav-container) + div + div button:hover {
        background: transparent !important;
        border: none !important;
        color: #4ECDC4 !important;
        text-decoration: underline !important;
        transform: none !important;
        box-shadow: none !important;
    }
    [data-testid="stVerticalBlock"] > div:has(.header-nav-container) + div + div button:disabled {
        background: transparent !important;
        border: none !important;
        color: #4ECDC4 !important;
        font-weight: 700 !important;
        opacity: 1 !important;
        cursor: not-allowed !important;
    }
    [data-testid="stVerticalBlock"] > div:has(.header-nav-container) + div + div button:focus {
        outline: none !important;
        box-shadow: none !important;
        background: transparent !important;
    }
    [data-testid="stVerticalBlock"] > div:has(.header-nav-container) + div + div button p {
        white-space: nowrap !important;
        margin: 0 !important;
    }
    /* Reduce top padding to halve the space */
    .block-container {
        padding-top: 1rem !important;
    }
    
    /* Reduce distance between text and line below */
    hr {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Create clickable text navigation with wider columns
    cols = st.columns([0.6, 0.15, 0.75, 5])

    with cols[0]:
        tutorial_clicked = st.button(
            "Tutorial",
            key="nav_tutorial_text",
            type="secondary",
            disabled=tutorial_active
        )
        if tutorial_clicked and not tutorial_active:
            st.session_state.app_mode = "Tutorial"
            st.session_state.current_step = 0
            st.rerun()

    with cols[1]:
        st.markdown("<p style='color: #6E7681; margin: 0; padding-top: 0.25rem; text-align: center;'>|</p>", unsafe_allow_html=True)

    with cols[2]:
        playground_clicked = st.button(
            "Playground",
            key="nav_playground_text",
            type="secondary",
            disabled=playground_active
        )
        if playground_clicked and not playground_active:
            st.session_state.app_mode = "Playground"
            st.rerun()

    # End navigation container
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Main content based on mode
    if st.session_state.app_mode == "Tutorial":
        # Progress Bar (showing on all steps except 0)
        if st.session_state.current_step > 0:
            progress = st.session_state.current_step / 6
            st.progress(progress)
            st.markdown(f"<p style='text-align:center; color:#8B949E; margin-bottom: 2rem;'>Step {st.session_state.current_step} of 6</p>", unsafe_allow_html=True)

        # Render current step from registry
        step_module = STEP_REGISTRY.get(st.session_state.current_step)
        if step_module:
            step_module.render()
        else:
            st.error(f"Step {st.session_state.current_step} not found in registry.")
    else:
        # Playground mode
        from steps.step_playground import render as render_playground
        render_playground()

if __name__ == "__main__":
    main()
