def compute_soil_saturation_component(
    soil_saturation_current: float,
) -> float:
    """
    Convert the current normalized soil saturation (S) into a base risk score.

    Inputs
    ------
    soil_saturation_current : float
        Normalized saturation index at ~50 cm depth near the foundation.
        - S ≈ 0   : very dry relative to field capacity / saturation.
        - S ≈ 1   : near the defined saturation point for this soil preset.
        - S > 1   : extremely wet (e.g., waterlogged / above design saturation).

    Approach
    --------
    - Below a small threshold (S < 0.2), we treat risk as effectively zero.
      The soil is too dry to sustain seepage-type pressure.
    - Between S = 0.2 and S = 1.0, risk increases roughly linearly.
    - Above S = 1.0, risk grows faster (soil is “very wet” and close
      to hydrostatic conditions).
    - We map the result into a base risk score from 0–100 that is used
      as the foundation for the final risk calculation.

    Returns
    -------
    base_risk_score : float
        Base risk score in the range [0, 100] driven only by soil saturation.
        This is *before* storm severity or site sensitivity amplification.
    """

    S = soil_saturation_current

    # Very dry soil: no meaningful seepage risk.
    if S <= 0.2:
        return 0.0

    # Moderate range: gradually increasing risk.
    if 0.2 < S <= 1.0:
        # Map S from [0.2, 1.0] -> base risk [0, 70]
        # 70 is a scaling choice to leave headroom for amplification.
        fraction = (S - 0.2) / (1.0 - 0.2)  # 0–1
        return fraction * 70.0

    # Very wet range: soil is above nominal saturation, risk rises quickly.
    # Clamp S at 1.5 to avoid unbounded growth from this component alone.
    S_capped = min(S, 1.5)
    # Map S from [1.0, 1.5] -> additional [70, 100]
    fraction = (S_capped - 1.0) / (1.5 - 1.0)  # 0–1
    return 70.0 + fraction * 30.0