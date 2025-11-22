from typing import Dict, Any


def compute_features(
    saturation_values: Dict[str, float],
    rain_6h_prev: float,
    rain_12h_forecast: float,
) -> Dict[str, Any]:
    """
    Compute simple, interpretable features for the flood-risk model
    from normalized saturation values and rainfall information.

    Inputs
    ------
    saturation_values : dict
        Normalized saturation values (S) for each sensor at the current timestep.
        Expected keys:
            "north_sensor",
            "south_sensor",
            "east_sensor",
            "west_sensor"
        These values come from normalize_moisture() and represent:
            S = (theta - THETA_FC) / (THETA_SAT - THETA_FC)

    rain_6h : float
        Total observed rainfall over the last 6 hours [mm],
        pre-computed in the pipeline.

    forecast_12h : float
        Total forecast rainfall over the next 12 hours [mm].

    Outputs
    -------
    features : dict
        A dictionary of higher-level features used by the risk model, including:
            - "sat_avg"    : average deep saturation around the house
            - "max_sat"      : maximum deep saturation at any wall
            - "sat_asymmetry"        : deep saturation asymmetry (max_deep - min_deep) - should eventually tell us which walls
            - "rain_6h_prev"       : 6-hour observed rainfall
            - "rain_12h_forecast"  : 12-hour forecast rainfall

        These are intentionally simple for v1 and can be extended later
        with trends and longer-term averages.
    """

    # 1. Extract saturation values by wall (assume keys exist)
    sat_north_sensor = float(saturation_values["north_sensor"])
    sat_south_sensor = float(saturation_values["south_sensor"])
    sat_east_sensor = float(saturation_values["east_sensor"])
    sat_west_sensor = float(saturation_values["west_sensor"])

    sat_values_list = [
        sat_north_sensor,
        sat_south_sensor,
        sat_east_sensor,
        sat_west_sensor,
    ]

    # 2. Perimeter averages
    sat_avg = sum(sat_values_list) / len(sat_values_list)

    # 3. Deep asymmetry: how uneven saturation is around the house
    max_sat = max(sat_values_list)
    min_sat = min(sat_values_list)
    sat_asymmetry = max_sat - min_sat

    # 4. Bundle everything into a feature dict
    features: Dict[str, Any] = {
        "sat_avg": sat_avg,
        "max_sat": max_sat,
        "sat_asymmetry": sat_asymmetry,
        "rain_6h_prev": float(rain_6h_prev),
        "rain_12h_forecast": float(rain_12h_forecast),
    }

    # Future extension ideas (not implemented yet):
    # - 3-hour shallow trend: how fast the shallow layer is wetting up
    # - 24-hour deep average: longer-term saturation persistence
    # - Per-wall features for localized risk (e.g., keep S_N_deep, S_S_deep, etc.)

    return features
