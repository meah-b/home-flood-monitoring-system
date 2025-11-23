from typing import Dict
from src.config import THETA_FC, THETA_SAT

def normalize_moisture(cleaned_readings: Dict[str, float]) -> Dict[str, float]:
    """
    Convert raw soil moisture values into a normalized saturation measure.

    Assumptions:
    -----------
    - cleaned_readings values are fractional volumetric water content (theta),
      typically between 0 and 1.
    - THETA_FC (field capacity) and THETA_SAT (saturation) are defined in config.py.

    Definition:
    -----------
    For each sensor value theta, we compute a normalized saturation:

        S = (theta - THETA_FC) / (THETA_SAT - THETA_FC)

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

    saturation: Dict[str, float] = {}

    for key, theta in cleaned_readings.items():
        #TODO: add lookup for soil-specific THETA_FC and THETA_SAT
        S = (theta - THETA_FC) / (THETA_SAT - THETA_FC)
        saturation[key] = S

    return saturation
