import streamlit as st

from schemas.asset_profile import AssetClass, AssetProfile


def render_dashboard(profiles: list[AssetProfile]) -> None:
    """
    Full acquisition targets table — sorted by fit score, filterable by
    asset class and minimum value. Top 3 get a priority badge.
    """
    st.subheader("Acquisition Targets")

    # ── Summary metrics bar 
    total = len(profiles)
    viable = sum(1 for p in profiles if p.value_threshold_met)
    avg_score = sum(p.sax_fit_score for p in profiles) / total if total else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Documents Processed", total)
    col2.metric("Viable Targets (>€20M)", viable)
    col3.metric("Avg Fit Score", f"{int(avg_score * 100)}%")

    st.divider()

    # ── Filters 
    with st.expander("Filters", expanded=False):
        col_a, col_b, col_c = st.columns(3)

        with col_a:
            class_options = ["All"] + [c.value for c in AssetClass]
            selected_class = st.selectbox("Asset Class", class_options)

        with col_b:
            min_score = st.slider("Minimum Fit Score", 0, 100, 0, step=5)

        with col_c:
            only_viable = st.checkbox("Only >€20M targets", value=False)

    # ── Apply filters
    filtered = profiles
    if selected_class != "All":
        filtered = [p for p in filtered if p.asset_class.value == selected_class]
    if min_score > 0:
        filtered = [p for p in filtered if p.sax_fit_score * 100 >= min_score]
    if only_viable:
        filtered = [p for p in filtered if p.value_threshold_met]

    if not filtered:
        st.warning("No targets match the current filters.")
        return

    st.caption(f"Showing {len(filtered)} of {total} documents")
    st.divider()

    # ── Target rows 
    for i, profile in enumerate(filtered):
        is_priority = i < 3
        score_pct = int(profile.sax_fit_score * 100)
        score_color = "#2ecc71" if score_pct >= 60 else "#e67e22" if score_pct >= 35 else "#e74c3c"

        # Row header — always visible
        col_badge, col_location, col_class, col_value, col_score, col_toggle = st.columns(
            [0.08, 0.25, 0.18, 0.18, 0.15, 0.16]
        )

        with col_badge:
            if is_priority:
                st.markdown('<span class="priority-badge">Priority</span>', unsafe_allow_html=True)

        with col_location:
            st.markdown(f"**{profile.location_city}**")
            st.caption(profile.location_address or profile.source_file)

        with col_class:
            st.markdown(profile.asset_class.value)

        with col_value:
            if profile.estimated_value_eur:
                st.markdown(f"€{profile.estimated_value_eur:,.0f}")
            else:
                st.caption("—")

        with col_score:
            st.markdown(
                f'<span style="color:{score_color}; font-weight:700;">{score_pct}%</span>',
                unsafe_allow_html=True,
            )

        with col_toggle:
            with st.expander("Details"):
                _render_profile_detail(profile)

        st.divider()


def _render_profile_detail(profile: AssetProfile) -> None:
    """
    Compact detail view shown when a dashboard row is expanded.
    Covers signals, conversion potential, and the acquisition rationale.
    """
    if profile.distress_signals:
        st.markdown("**Distress Signals**")
        for signal in profile.distress_signals:
            st.markdown(f"- {signal}")

    if profile.zoning_flags:
        st.markdown("**Zoning Flags**")
        for flag in profile.zoning_flags:
            st.markdown(f"- {flag}")

    if profile.conversion_potential:
        st.markdown("**Conversion Potential**")
        st.markdown(", ".join(c.value for c in profile.conversion_potential))

    if profile.summary:
        st.markdown("**Rationale**")
        st.info(profile.summary)