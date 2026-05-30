import streamlit as st


def inject_styles() -> None:
    """
    Injects custom CSS into the Streamlit app.
    Called once from app/main.py at startup.
    Keeps all visual styling in one place — easy to tweak before the demo.
    """
    st.markdown("""
        <style>
            /* ── General ── */
            html, body, [class*="css"] {
                font-family: 'Inter', sans-serif;
            }

            h1 {
                font-weight: 700;
                letter-spacing: -0.5px;
            }

            /* ── Raw document box (Screen A) ── */
            .raw-document-box {
                background-color: #1a1a1a;
                color: #a0a0a0;
                font-family: 'Courier New', monospace;
                font-size: 0.78rem;
                line-height: 1.7;
                padding: 1.25rem 1.5rem;
                border-radius: 6px;
                border-left: 4px solid #444;
                white-space: pre-wrap;
                word-break: break-word;
                max-height: 420px;
                overflow-y: auto;
            }

            /* ── Fit score box (Screen B) ── */
            .fit-score-box {
                display: flex;
                align-items: center;
                justify-content: space-between;
                background-color: #111111;
                padding: 1rem 1.5rem;
                border-radius: 6px;
                margin-bottom: 0.5rem;
            }

            .fit-score-label {
                font-size: 0.85rem;
                color: #888;
                text-transform: uppercase;
                letter-spacing: 0.08em;
            }

            .fit-score-value {
                font-size: 2rem;
                font-weight: 700;
                letter-spacing: -1px;
            }

            /* ── Dashboard table rows ── */
            .target-row {
                background-color: #111;
                border-radius: 6px;
                padding: 0.85rem 1rem;
                margin-bottom: 0.4rem;
                border-left: 3px solid #333;
                transition: border-color 0.2s ease;
            }

            .target-row:hover {
                border-left-color: #555;
            }

            .target-row.priority {
                border-left-color: #2ecc71;
            }

            /* ── Priority badge ── */
            .priority-badge {
                background-color: #1a3a2a;
                color: #2ecc71;
                font-size: 0.7rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                padding: 2px 8px;
                border-radius: 20px;
                display: inline-block;
            }

            /* ── Metric overrides ── */
            [data-testid="stMetricValue"] {
                font-size: 1rem;
                font-weight: 600;
            }

            /* ── Divider ── */
            hr {
                border-color: #222;
                margin: 1rem 0;
            }

            /* ── Scrollbar for raw document box ── */
            .raw-document-box::-webkit-scrollbar {
                width: 4px;
            }

            .raw-document-box::-webkit-scrollbar-track {
                background: #111;
            }

            .raw-document-box::-webkit-scrollbar-thumb {
                background: #333;
                border-radius: 4px;
            }
        </style>
    """, unsafe_allow_html=True)