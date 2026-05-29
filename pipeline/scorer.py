from schemas.asset_profile import AssetProfile, ConversionPotential

# These are the conversion types SAX actively targets based on their portfolio.
# A profile matching more of these scores higher — it's a simple overlap check,
SAX_TARGET_CONVERSIONS = {
    ConversionPotential.MICRO_APARTMENTS,
    ConversionPotential.BOUTIQUE_HOTEL,
    ConversionPotential.ASSISTED_LIVING,
    ConversionPotential.SERVICED_APARTMENTS,
}

# Distress keywords that signal an off-market or motivated seller situation.
# The more of these present, the more likely SAX can move before competitors.
HIGH_VALUE_DISTRESS_SIGNALS = {
    "insolvency",
    "liquidation",
    "vacancy",
    "restructuring",
    "receivership",
    "balance sheet",
}


def compute_score(profile: AssetProfile) -> float:
    """
    Score a profile from 0.0 to 1.0 based on SAX's investment criteria.
    No LLM involved — just deterministic rules against the extracted fields.

    Breakdown:
        0.40  — value threshold (the hard filter, biggest weight)
        0.25  — conversion potential overlap with SAX target use cases
        0.20  — distress signals present (off-market opportunity indicator)
        0.15  — zoning risk penalty (flags reduce the score)
    """
    score = 0.0

    # Value threshold — binary, either it clears €20M or it doesn't
    if profile.value_threshold_met:
        score += 0.40

    # Conversion potential — partial credit for partial overlap
    if profile.conversion_potential:
        matched = SAX_TARGET_CONVERSIONS & set(profile.conversion_potential)
        overlap_ratio = len(matched) / len(SAX_TARGET_CONVERSIONS)
        score += 0.25 * overlap_ratio

    # Distress signals — check how many high-value keywords appear
    if profile.distress_signals:
        combined = " ".join(profile.distress_signals).lower()
        hits = sum(1 for kw in HIGH_VALUE_DISTRESS_SIGNALS if kw in combined)
        distress_ratio = min(hits / len(HIGH_VALUE_DISTRESS_SIGNALS), 1.0)
        score += 0.20 * distress_ratio

    # Zoning risk — each flag shaves a small amount off the final score
    if profile.zoning_flags:
        penalty = min(len(profile.zoning_flags) * 0.03, 0.15)
        score -= penalty

    return round(max(score, 0.0), 3)


def score_profile(profile: AssetProfile) -> AssetProfile:
    """
    Compute and attach the sax_fit_score to a profile in place.
    Returns the same profile object so it can be chained in the pipeline.
    """
    profile.sax_fit_score = compute_score(profile)
    return profile