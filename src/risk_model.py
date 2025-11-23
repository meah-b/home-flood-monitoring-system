"""
risk_model.py
Core risk model combining soil saturation, storm severity, and site sensitivity and mapping to user-facing categories.

Assumptions
-----------
- All data has already passed through quality control and basic smoothing.
- Soil moisture values have already been converted to a normalized saturation
  index S for the relevant depth (~50 cm) based on the selected soil preset
  (field capacity, wilting point, saturation).
- We are only modeling seepage / hydrostatic pressure type basement risk,
  not sewer backup or surface overland flooding.
- storm_severity_ratio and soil_response_sensitivity_index are already
  pre-computed elsewhere in the pipeline from historical data.
"""
from soil_saturation import compute_soil_saturation_component
from storm_severity import compute_storm_severity_component
from site_sensitivity import compute_site_sensitivity_component

from typing import Tuple


def compute_risk_score(
    soil_saturation_current: float,
    soil_saturation_1h_ago: float,
    forecast_24h_mm: float,
    IDF_24h_2yr_mm: float,
) -> Tuple[float, float]:
    """
    Compute the internal and displayed risk scores from the three components.

    Structure
    --------
    1. Compute a base soil risk score [0, 100] from saturation alone.
    2. Compute storm_severity_factor [0, 1.5] from forecast / IDF ratio.
    3. Compute site_sensitivity_factor [0, 1] from the last hour of soil behavior.
    4. Combine them multiplicatively:

           RiskInternal = BaseSoilRisk * (1 + site_sensitivity_factor
                                              * storm_severity_factor)

       This means:
         - If soil is very dry, RiskInternal stays low even for big storms.
         - If soil is wet but storms are small, RiskInternal is mostly
           determined by saturation.
         - If soil is wet, the site is reactive, and a severe storm is coming,
           RiskInternal can exceed 100 internally (extreme conditions).

    5. RiskDisplayed is then clamped to [0, 100] for user-facing simplicity.

    Returns
    -------
    risk_score_internal : float
        Raw hazard index that may exceed 100 in extreme conditions.
    risk_score_displayed : float
        Risk score clamped to [0, 100] for mapping to user categories.
    """

    base_soil_risk = compute_soil_saturation_component(soil_saturation_current)
    storm_factor = compute_storm_severity_component(forecast_24h_mm, IDF_24h_2yr_mm)
    site_sensitivity_factor = compute_site_sensitivity_component(
        soil_saturation_current, soil_saturation_1h_ago
    )

    amplification_factor = 1.0 + site_sensitivity_factor * storm_factor
    risk_score_internal = base_soil_risk * amplification_factor

    # Clamp for the user-facing score.
    risk_score_displayed = max(0.0, min(risk_score_internal, 100.0))

    return risk_score_internal, risk_score_displayed


def map_risk_category(risk_score_displayed: float) -> str:
    """
    Map the displayed risk score (0–100) into a user-facing category.

    Categories and meanings
    -----------------------
    Low (0–30)
        Soil/risk:
            - Soil near the foundation is relatively dry or only mildly wet.
            - Upcoming rainfall is small or typical for the area.
        User:
            - Basement seepage due to soil pressure is unlikely.
            - No action needed beyond normal seasonal maintenance.

    Moderate (30–60)
        Soil/risk:
            - Soil moisture is elevated compared to normal background levels,
              OR a moderate storm is coming.
            - Conditions are trending wetter, but not yet critical.
        User:
            - Start paying attention.
            - Check gutters, downspouts, and sump pump function if present.

    High (60–80)
        Soil/risk:
            - Soil around the foundation is quite wet and the model indicates
              a meaningful increase in hydrostatic pressure is likely,
              especially with the incoming storm.
        User:
            - Take preventative steps:
                - Move valuables off the basement floor.
                - Confirm sump pump operation.
                - Monitor known problem spots (cracks, window wells).

    Severe (80–100)
        Soil/risk:
            - Soil is near or above saturation and the upcoming rainfall
              is unusually large for this location (e.g., near or above a
              2-year event).
            - There is a significant chance of seepage at weak points if
              conditions persist.
        User:
            - Treat as a “prepare now” situation:
                - Protect items in at-risk areas.
                - Monitor basement during/after the storm.
                - Consider additional temporary measures if you’ve had
                  issues here before.

    Parameters
    ----------
    risk_score_displayed : float
        Risk score after clamping to [0, 100].

    Returns
    -------
    category : str
        One of "Low", "Moderate", "High", "Severe".
    """

    score = risk_score_displayed

    if score < 30.0:
        return "Low"
    elif score < 60.0:
        return "Moderate"
    elif score < 80.0:
        return "High"
    else:
        return "Severe"
