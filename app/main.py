import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st

from app.components.styles import inject_styles
from app.views.dashboard import render_dashboard
from app.views.screen_a_raw import render_screen_a
from app.views.screen_b_profile import render_screen_b
from pipeline.loader import load_documents
from pipeline.extractor import extract_profile
from pipeline.scorer import score_profile
from pipeline.storage import get_all, init_db

st.set_page_config(
    page_title="SAX Sourcing Engine",
    page_icon="🏢",
    layout="wide",
)

inject_styles()
init_db()


def main():
    st.title("SAX-Gruppe — Market Sourcing Engine")
    st.caption("Automated acquisition intelligence across Baden-Württemberg")

    tab_pipeline, tab_targets = st.tabs(["🔍 Live Pipeline", "📋 Acquisition Targets"])

    # --- Tab 1: The demo flow ---
    with tab_pipeline:
        st.subheader("Document Intelligence")
        st.write("Select a raw source document to see how the pipeline structures it.")

        documents = load_documents()
        if not documents:
            st.warning("No documents found in corpus/. Add .txt files and re-run.")
            return

        filenames = [filename for filename, _ in documents]
        doc_map = {filename: text for filename, text in documents}

        # Default to the first doc — swap index for whichever looks best in the demo
        selected = st.selectbox("Source document", filenames, index=0)
        raw_text = doc_map[selected]

        col_a, col_b = st.columns(2)

        with col_a:
            render_screen_a(raw_text)

        with col_b:
            if st.button("Extract with AI ✦", use_container_width=True):
                with st.spinner("Extracting acquisition profile..."):
                    profile = extract_profile(selected, raw_text)

                if profile is None:
                    st.error("Extraction failed. Check your API key and try again.")
                else:
                    profile = score_profile(profile)
                    st.session_state["last_profile"] = profile

            if "last_profile" in st.session_state:
                render_screen_b(st.session_state["last_profile"])

    # Tab 2: Full ranked target table
    with tab_targets:
        profiles = get_all()
        if not profiles:
            st.info("No profiles in the database yet. Run the pipeline first: python scripts/run_pipeline.py")
        else:
            render_dashboard(profiles)


if __name__ == "__main__":
    main()