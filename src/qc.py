from typing import Dict


def QC_and_smooth(raw_readings: Dict[str, float]) -> Dict[str, float]:
    """
    Placeholder QC and smoothing function.
    
    For early development, we simply return the raw readings without modification.
    The dataset is assumed to be clean, within expected ranges, and without sensor errors.

    Future QC TODOs:
    ----------------
    1. Range validation
       - Soil moisture readings are expected to be between 0 and 1 (fractional volumetric water content).
       - Flag values outside this range as sensor errors.

    2. Missing / NaN handling
       - Detect NaN, None, empty strings, or failed conversions.
       - Decide whether to use previous timestep values or fall back to defaults.

    3. Outlier detection
       - Detect abrupt spikes or drops (e.g., sensor glitches).
       - Possibly apply a small threshold-based smoothing or replacement.

    4. Temporal smoothing (optional)
       - Very light smoothing (moving average) to reduce noise.
       - Only if it does not reduce responsiveness to rainfall-driven changes.

    5. Per-sensor health monitoring (future feature)
       - Track frequent failures or drift for each sensor.
       - Could output warnings or mark a sensor as unreliable.

    For now:
    --------
    - We trust the dataset.
    - We perform no validation, filtering, or smoothing.
    - We return the raw readings unchanged so the pipeline can run end-to-end.

    Parameters
    ----------
    raw_readings : dict
        Keys:
        "N_shallow", "N_deep",
        "S_shallow", "S_deep",
        "E_shallow", "E_deep",
        "W_shallow", "W_deep".

    Returns
    -------
    dict
        The raw readings, unchanged.
    """

    # Return raw values directly (no QC applied yet)
    return raw_readings
