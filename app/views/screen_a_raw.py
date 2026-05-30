import streamlit as st


def render_screen_a(raw_text: str) -> None:
    """
    Screen A — The Problem.
    Shows the raw unstructured source document exactly as ingested.
    Styled to feel overwhelming on purpose — this is the before.
    """
    st.markdown("#### 📄 Raw Source Document")
    st.caption("Unstructured text as ingested from the source — insolvency notice, zoning filing, or broker listing.")

    st.markdown(
        f"""
        <div class="raw-document-box">
            {raw_text}
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_left, col_right = st.columns(2)
    with col_left:
        st.metric("Characters", f"{len(raw_text):,}")
    with col_right:
        st.metric("Words", f"{len(raw_text.split()):,}")