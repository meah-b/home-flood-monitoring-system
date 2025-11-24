import pandas as pd

def compute_site_sensitivity_component(
    soil_saturation_current: float,
    soil_saturation_1h_ago: float,
) -> float:
    """
    Compute a short-term site sensitivity index based solely on the
    *last 1 hour* of soil saturation change.

    Idea
    ----
    Sensitivity = "How fast has soil saturation increased in the last hour?"

    We compute:
        ΔS_1h = max(0, S_now - S_1h_ago)

    Then map ΔS_1h into [0, 1] using a reference:
        - ΔS_1h = 0.0  → index = 0.0  (soil not responding)
        - ΔS_1h = 0.05 → index ≈ 0.5  (moderate increase)
        - ΔS_1h ≥ 0.1 → index = 1.0  (highly reactive in this storm)

    Parameters
    ----------
    soil_saturation_current : float
        Current normalized soil saturation (0 = at FC, 1 = at SAT).

    soil_saturation_1h_ago : float
        Normalized soil saturation 1 hour ago (0 = at FC, 1 = at SAT).

    Returns
    -------
    sensitivity_index : float in [0, 1]
    """

    # Only consider wetting (positive increases)
    delta_S_1h = max(0.0, soil_saturation_current - soil_saturation_1h_ago)

    # DELTA_S_REF = 0.1 means: a 10% jump toward saturation in 1 hour
    DELTA_S_REF = 0.1
    sensitivity_index = delta_S_1h / DELTA_S_REF

    # Clamp to [0, 1]
    return max(0.0, min(sensitivity_index, 1.0))