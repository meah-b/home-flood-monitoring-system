from typing import Dict, List, Optional
import math


def _reading_passes_basic_qc(reading: Dict[str, float]) -> bool:
    """
    Basic QC for a single raw reading.

    Conditions (v1):
    - All sensor values must be real numbers (no None, no NaN).
    - All values must lie within [0, 1] as fractional volumetric water content.

    If any sensor fails these checks, the entire reading is rejected.
    """

    for _, value in reading.items():
        # Reject missing values
        if value is None:
            return False

        # Reject non-float-ish or NaN
        try:
            v = float(value)
        except (TypeError, ValueError):
            return False

        if math.isnan(v):
            return False

        if not (0.0 <= v <= 1.0):
            return False

    return True


def QC_and_smooth(
    batch_readings: List[Dict[str, float]],
    previous_valid_reading: Optional[Dict[str, float]] = None,
) -> Dict[str, float]:
    """
    Quality control for a batch of readings at a single 15-minute interval.

    Inputs
    ------
    batch_readings : list of dict
        A list of raw readings taken within the same 15-minute window.
        Each element is a dict like:
            {
                "north_sensor": float,
                "south_sensor": float,
                "east_sensor": float,
                "west_sensor": float,
            }
        The first reading in the list is the earliest; we prefer to keep
        ordering simple: try the first, then the second, etc.

    previous_valid_reading : dict or None
        The last known good reading from an earlier timestep.
        Used as a fallback if all readings in this batch fail QC.

    Behavior
    --------
    1. Iterate over each reading in the batch in order:
         - Run basic QC (range checks, NaNs).
         - As soon as one passes, return it as the cleaned reading.

    2. If all readings fail QC:
         - If previous_valid_reading is provided, return that.
         - Otherwise, you can either:
             - raise an error, or
             - return an empty dict / special marker.

       For now, we fall back to previous_valid_reading if possible,
       and raise a ValueError if there is truly nothing to use.
    """

    # 1. Try each reading in order and return the first that passes QC.
    for reading in batch_readings:
        if _reading_passes_basic_qc(reading):
            return reading

    # 2. If we get here, all readings failed QC.
    #    Fall back to the last known valid reading if available.
    if previous_valid_reading is not None:
        return previous_valid_reading

    # 3. No valid reading and no fallback available: this is a hard failure.
    #    You can change this to return {} if you prefer a softer behavior.
    #    TODO: better handling for missing data
    raise ValueError(
        "QC_and_smooth: all readings failed QC and no previous_valid_reading was provided."
    )
