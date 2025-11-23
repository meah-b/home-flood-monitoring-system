def compute_storm_severity_component(
    forecast_24h_mm: float,
    IDF_24h_2yr_mm: float,
) -> float:
    """
    Convert storm severity into a dimensionless storm impact factor.

    Inputs
    ------
    storm_severity_ratio : float
        Ratio of forecast rainfall over the chosen horizon (e.g. 24h)
        to the local IDF baseline (e.g. 24h 2-year storm depth):

            storm_severity_ratio = forecast_24h_mm / IDF_24h_2yr_mm

        Examples:
        - 0.3  : small event, well below typical design storm
        - 1.0  : equal to a 2-year 24h storm
        - 1.5+ : larger than a 2-year event (unusually severe)

    Approach
    --------
    We map the ratio into a factor in [0, 1.5]:

    - Ratios below 0.3 contribute almost no additional risk.
    - Ratios between 0.3 and 1.0 increase risk linearly up to 1.0.
    - Ratios above 1.0 up to 1.5 get an extra boost up to 1.5.
      (Values > 1.5 are capped at 1.5 for now.)

    Returns
    -------
    storm_factor : float
        Dimensionless factor in [0, 1.5] representing how much this storm
        is capable of increasing risk, *relative* to the local climate.
        This factor will be combined with site sensitivity to adjust
        the base soil risk.
    """
    storm_severity_ratio = forecast_24h_mm / IDF_24h_2yr_mm

    if storm_severity_ratio <= 0.3:
        # Very small event relative to local climate → negligible extra risk.
        return 0.0

    if 0.3 < storm_severity_ratio <= 1.0:
        # Map [0.3, 1.0] -> [0.0, 1.0]
        return (storm_severity_ratio - 0.3) / (1.0 - 0.3)

    # storm_severity_ratio > 1.0
    ratio_capped = min(storm_severity_ratio, 1.5)
    # Map [1.0, 1.5] -> [1.0, 1.5]
    return 1.0 + (ratio_capped - 1.0) / (1.5 - 1.0) * 0.5