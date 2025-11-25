from typing import Dict, List, Optional
import math
from statistics import median


def _reading_passes_basic_qc(reading: Dict[str, float]) -> bool:
    """
    Basic QC for a single raw reading.

    Conditions (v1):
    - All sensor values must be real numbers (no None, no NaN).
    - All values must lie within [0, 1] as fractional volumetric water content.
    - TODO: check timestamp

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

    Now actually uses the whole batch:

    1. Filter to readings that pass basic QC (no NaN, 0–1 range).
    2. If any survive, compute a smoothed reading by taking the
       *per-sensor median* across valid readings.
    3. If all readings fail QC:
         - If previous_valid_reading is provided, return that.
         - Otherwise raise ValueError.
    """

    if not batch_readings:
        if previous_valid_reading is not None:
            return previous_valid_reading
        raise ValueError("QC_and_smooth: no readings provided and no previous_valid_reading.")

    # 1. Keep only readings that pass QC
    valid_readings = [r for r in batch_readings if _reading_passes_basic_qc(r)]

    # 2. If we have at least one valid reading, smooth via per-sensor median
    if valid_readings:
        smoothed: Dict[str, float] = {}
        sensor_keys = valid_readings[0].keys()

        for key in sensor_keys:
            values = [float(r[key]) for r in valid_readings]
            smoothed[key] = float(median(values))

        return smoothed

    # 3. If all readings failed QC, fall back if possible
    if previous_valid_reading is not None:
        return previous_valid_reading

    raise ValueError(
        "QC_and_smooth: all readings failed QC and no previous_valid_reading was provided."
    )
