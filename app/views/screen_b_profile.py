import streamlit as st

from app.components.rule_checker import render_rule_checks
from schemas.asset_profile import AssetProfile


def render_screen_b(profile: AssetProfile) -> None:
    """
    Screen B — The Solution.
    Renders the AI-extracted AssetProfile as a clean, actionable table.
    This is the moment in the demo — say nothing and let them read it.
    """
    st.markdown("#### 🏢 AI Extracted Asset Profile")
    st.caption("Structured acquisition intelligence extracted from the raw document above.")

    # Fit score front and center — it's the first number they should see
    score_pct = int(profile.sax_fit_score * 100)
    score_color = "#2ecc71" if score_pct >= 60 else "#e67e22" if score_pct >= 35 else "#e74c3c"

    st.markdown(
        f"""
        <div class="fit-score-box" style="border-left: 4px solid {score_color};">
            <span class="fit-score-label">SAX Fit Score</span>
            <span class="fit-score-value" style="color: {score_color};">{score_pct}%</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # Core property parameters
    st.markdown("**Location & Asset**")
    col_a, col_b = st.columns(2)
    with col_a:
        st.text_input("City", value=profile.location_city, disabled=True)
        st.text_input("Asset Class", value=profile.asset_class.value, disabled=True)
        plot = f"{profile.plot_size_sqm:,.0f} sqm" if profile.plot_size_sqm else "Not extracted"
        st.text_input("Plot Size", value=plot, disabled=True)

    with col_b:
        address = profile.location_address or "Not extracted"
        st.text_input("Address", value=address, disabled=True)
        gfa = f"{profile.building_size_sqm:,.0f} sqm" if profile.building_size_sqm else "Not extracted"
        st.text_input("Building Size (GFA)", value=gfa, disabled=True)
        value = f"€{profile.estimated_value_eur:,.0f}" if profile.estimated_value_eur else "Not extracted"
        st.text_input("Estimated Value", value=value, disabled=True)

    st.divider()

    # Signals and flags
    st.markdown("**Risk & Opportunity Signals**")
    col_c, col_d = st.columns(2)
    with col_c:
        st.markdown("🔴 **Distress Signals**")
        if profile.distress_signals:
            for signal in profile.distress_signals:
                st.markdown(f"- {signal}")
        else:
            st.caption("None identified")

    with col_d:
        st.markdown("⚠️ **Zoning Flags**")
        if profile.zoning_flags:
            for flag in profile.zoning_flags:
                st.markdown(f"- {flag}")
        else:
            st.caption("None identified")

    st.divider()

    # Conversion potential
    st.markdown("**Conversion Potential**")
    if profile.conversion_potential:
        cols = st.columns(len(profile.conversion_potential))
        for col, conversion in zip(cols, profile.conversion_potential):
            col.success(conversion.value)
    else:
        st.caption("No conversion potential identified")

    st.divider()

    # SAX investment rule checks
    st.markdown("**Investment Rule Checks**")
    render_rule_checks(profile)

    st.divider()

    # LLM-generated acquisition rationale
    st.markdown("**Acquisition Rationale**")
    st.info(profile.summary if profile.summary else "No summary generated.")