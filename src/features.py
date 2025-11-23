from typing import Dict, Any


def compute_features(
    saturation_values: Dict[str, float],
    forecast_24h_mm: float,
    soil_saturation_1h_ago: float,
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

    forecast_24h_mm : float
        Total forecast rainfall over the next 24 hours [mm].

    Outputs
    -------
    features : dict
        A dictionary of higher-level features used by the risk model, including:
            - "sat_avg"    : average deep saturation around the house
            - "max_sat"      : maximum deep saturation at any wall
            - "sat_asymmetry"        : deep saturation asymmetry (max_deep - min_deep)
            - "rain_24h_forecast"  : 24-hour forecast rainfall

        These are intentionally simple for v1 and can be extended later
        with trends and longer-term averages.
    """

    # 1. Extract saturation values by wall (assume keys exist)
    sat_north_sensor = float(saturation_values["north_sensor"])
    sat_south_sensor = float(saturation_values["south_sensor"])
    sat_east_sensor = float(saturation_values["east_sensor"])
    sat_west_sensor = float(saturation_values["west_sensor"])

    sat_by_wall = {
        "north": sat_north_sensor,
        "south": sat_south_sensor,
        "east":  sat_east_sensor,
        "west":  sat_west_sensor,
    }

    # 2. Perimeter average
    sat_values = list(sat_by_wall.values())
    sat_avg = sum(sat_values) / len(sat_values)

    # 3. Asymmetry
    max_sat = max(sat_values)
    wettest_side = next(
        wall for wall, value in sat_by_wall.items() if value == max_sat
    )    
    min_sat = min(sat_values)
    asym_value = max_sat - min_sat

    asymmetry_dict = {
        "value": asym_value,
        "max_sat": max_sat,
        "wettest_side": wettest_side,
    }

    # 4. TODO: add logic to fetch the IDF value for the location
    IDF_24h_2yr_mm = 50.0  # Placeholder value; replace with actual lookup

    # 5. Bundle everything into a feature dict
    features: Dict[str, Any] = {
        "sat_avg": sat_avg,
        "asymmetry": asymmetry_dict,
        "forecast_24h_mm": forecast_24h_mm,
        "IDF_24h_2yr_mm": IDF_24h_2yr_mm,
        "soil_saturation_1h_ago": soil_saturation_1h_ago,
    }

    return features
