from typing import Dict


def compute_risk_score(features: Dict[str, float]) -> float:
    """
    Compute a 0–100 flood risk score from engineered features.

    Inputs (from features dict)
    ---------------------------
    sat_avg : float
        Average deep saturation around the house (unitless S).
    max_sat : float
        Maximum deep saturation at any wall.
    sat_asymmetry : float
        Deep saturation asymmetry: max_deep - min_deep.
    rain_6h_prev : float
        Total observed rainfall over the last 6 hours [mm].
        NOTE: currently NOT used in the risk score. Kept for analysis/calibration.
    rain_12h_forecast : float
        Total forecast rainfall over the next 12 hours [mm].
        Used to modulate how urgent the current saturation state is.

    Approach
    --------
    1. Baseline seepage risk:
       - Driven mainly by S_deep_avg and max_deep.
       - Represents how loaded the soil is around the foundation.

    2. Forecast factor:
       - Uses forecast_12h only.
       - Scales the baseline risk up or down depending on how much rain is expected.

    3. Asymmetry risk:
       - Small additional bump if one wall is much wetter than the others.

    The result is clamped to [0, 100].
    """

    sat_avg = float(features["sat_avg"])
    max_sat = float(features["max_sat"])
    sat_asymmetry = float(features["sat_asymmetry"])
    # rain_6h_prev is currently unused but kept for future analysis
    # rain_6h_prev = float(features["rain_6h_prev"])
    rain_12h_forecast = float(features["rain_12h_forecast"])

    # -----------------------------
    # 1. Baseline seepage component
    # -----------------------------
    # Map S_deep_avg into ~0–80 points.
    # sat_avg ~ 0   -> near 0 baseline points
    # sat_avg ~ 1   -> ~80 baseline points
    baseline_raw = max(sat_avg, 0.0) * 80.0
    if baseline_raw > 80.0:
        baseline_raw = 80.0

    # If any wall is very wet at depth, add a small bump
    if max_sat > 1.0:
        baseline_raw += 5.0

    if baseline_raw > 85.0:
        baseline_raw = 85.0

    # -----------------------------
    # 2. Forecast factor
    # -----------------------------
    # Idea: future rain determines how urgent the current soil state is.
    # Assume "typical" forecast range ~0–40 mm in 12h for scaling.
    forecast_norm = min(rain_12h_forecast / 40.0, 1.0)  # 0–1

    # If no rain is expected, we still keep some fraction of the baseline
    # (risk of seepage when soil is already very wet), but lower urgency.
    # If heavy rain is expected, we apply the full baseline.
    storm_factor = 0.5 + 0.5 * forecast_norm  # ranges from 0.5 to 1.0

    combined = baseline_raw * storm_factor

    # -----------------------------
    # 3. Asymmetry component
    # -----------------------------
    asym_raw = 0.0
    if max_sat > 0.5 and sat_asymmetry > 0.1:
        # Limit sat_asymmetry to 0.5 for scaling; map to 0–10 points
        A_scaled = min(sat_asymmetry, 0.5) / 0.5  # 0–1
        asym_raw = A_scaled * 10.0

    # -----------------------------
    # 4. Combine and clamp
    # -----------------------------
    raw_score = combined + asym_raw

    if raw_score < 0.0:
        raw_score = 0.0
    elif raw_score > 100.0:
        raw_score = 100.0

    return raw_score


def map_risk_category(risk_score: float) -> str:
    """
    Map a numeric risk score (0–100) to a simple category string.
    """

    if risk_score < 30.0:
        return "Low"
    elif risk_score < 60.0:
        return "Moderate"
    elif risk_score < 80.0:
        return "High"
    else:
        return "Severe"
