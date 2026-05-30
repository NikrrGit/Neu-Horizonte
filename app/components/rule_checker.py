import streamlit as st

from schemas.asset_profile import AssetProfile


def render_rule_checks(profile: AssetProfile) -> None:
    """
    Renders a clean table of SAX's investment rules against the extracted profile.
    Each rule gets a pass/fail indicator and a human-readable reason.
    """
    rules = _evaluate_rules(profile)

    for rule in rules:
        col_check, col_name, col_reason = st.columns([0.08, 0.35, 0.57])
        with col_check:
            st.markdown(rule["icon"])
        with col_name:
            st.markdown(f"**{rule['name']}**")
        with col_reason:
            st.caption(rule["reason"])


def _evaluate_rules(profile: AssetProfile) -> list[dict]:
    """
    Run each investment rule against the profile and return
    a list of result dicts ready for rendering.
    """
    rules = []

    # Rule 1 — Volume threshold
    if profile.value_threshold_met:
        reason = f"€{profile.estimated_value_eur:,.0f} — clears the €20M threshold"
    elif profile.estimated_value_eur:
        reason = f"€{profile.estimated_value_eur:,.0f} — below the €20M threshold"
    else:
        reason = "Estimated value could not be extracted"
    rules.append({
        "icon": "✅" if profile.value_threshold_met else "❌",
        "name": "Volume > €20M",
        "reason": reason,
    })

    # Rule 2 — Region match
    baw_cities = {
        "tübingen", "stuttgart", "mannheim", "karlsruhe", "freiburg",
        "heidelberg", "ulm", "heilbronn", "reutlingen", "konstanz",
    }
    city_match = profile.location_city.lower() in baw_cities
    rules.append({
        "icon": "✅" if city_match else "⚠️",
        "name": "Core Focus Region",
        "reason": f"{profile.location_city} — {'within Baden-Württemberg target market' if city_match else 'outside primary focus region, verify manually'}",
    })

    # Rule 3 — Conversion potential
    has_conversion = len(profile.conversion_potential) > 0
    conversion_list = ", ".join(c.value for c in profile.conversion_potential) if has_conversion else None
    rules.append({
        "icon": "✅" if has_conversion else "❌",
        "name": "Conversion Potential",
        "reason": conversion_list if has_conversion else "No viable conversion use case identified",
    })

    # Rule 4 — Distress / off-market signal
    has_distress = len(profile.distress_signals) > 0
    rules.append({
        "icon": "✅" if has_distress else "⚠️",
        "name": "Off-Market Signal",
        "reason": profile.distress_signals[0] if has_distress else "No distress signals found — likely an open-market listing",
    })

    # Rule 5 — Zoning risk
    clean_zoning = len(profile.zoning_flags) == 0
    flag_summary = ", ".join(profile.zoning_flags) if profile.zoning_flags else None
    rules.append({
        "icon": "✅" if clean_zoning else "⚠️",
        "name": "Zoning Risk",
        "reason": "No blocking zoning flags identified" if clean_zoning else f"Flags present: {flag_summary}",
    })

    return rules