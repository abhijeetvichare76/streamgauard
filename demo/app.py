import streamlit as st
from styles.css import load_custom_css
from steps import STEP_REGISTRY

def main():
    # Page configuration
    st.set_page_config(
        page_title="StreamGuard Aegis",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Load custom CSS
    load_custom_css()

    # Initialize current step
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0

    # Progress Bar (optional, showing on all steps except 0)
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

if __name__ == "__main__":
    main()
