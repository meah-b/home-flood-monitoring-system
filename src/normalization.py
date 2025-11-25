from turtle import pd
from typing import Dict

import pandas as pd

def normalize_moisture(cleaned_readings: Dict[str, float], soil_type: str) -> Dict[str, float]:
    """
    Convert raw soil moisture values into a normalized saturation measure.

    Assumptions:
    -----------
    - cleaned_readings values are fractional volumetric water content (vwc),
      typically between 0 and 1.
    - fc_vwc (field capacity) and sat_vwc (saturation) are defined in config.py.

    Definition:
    -----------
    For each sensor value vwc, we compute a normalized saturation:

        S = (vwc - fc_vwc) / (sat_vwc - fc_vwc)

    Interpretation:
    ---------------
    - S = 0   -> at field capacity (or below)
    - S = 1   -> at saturation (or above)
    - S < 0   -> drier than field capacity
    - S > 1   -> wetter than the nominal saturation (could indicate pooling or model mismatch)

    We DO NOT clamp S in this function so we can see when values fall outside
    the expected range. Any decisions about how to handle very high or low
    values should be made in the risk model.

    Parameters
    ----------
    cleaned_readings : dict
        Current timestep's cleaned soil moisture values (theta) with keys like:
        "N_shallow", "N_deep", "S_shallow", "S_deep",
        "E_shallow", "E_deep", "W_shallow", "W_deep".

    Returns
    -------
    dict
        Normalized saturation values with the same keys. Values are unitless.
    """
    soil_water_properties = pd.read_csv(f"data/soil_water_properties.csv")
    row = soil_water_properties.loc[soil_water_properties['soil_type'] == soil_type]

    if row.empty:
        raise ValueError(f"Soil type '{soil_type}' not found")

    fc_vwc = float(row["fc_vwc"].values[0])
    sat_vwc = float(row["sat_vwc"].values[0])

    saturation: Dict[str, float] = {}

    for key, vwc in cleaned_readings.items():
        S = (vwc - fc_vwc) / (sat_vwc - fc_vwc)
        saturation[key] = S

    return saturation
