from src.qc import QC_and_smooth
from src.normalization import normalize_moisture
from src.features import compute_features
from src.risk_model import compute_risk_score, map_risk_category

import pandas as pd
from typing import Literal


def load_timeseries(risk_level: Literal["low", "moderate", "high"] = "low"):
    """Load soil moisture, observed rainfall, and forecast rainfall,
    merge them on timestamp, and compute 6h cumulative rainfall.
    """

    soil = pd.read_csv(f"data/{risk_level}_risk/soil_moisture_timeseries.csv", parse_dates=["timestamp"])
    rain_obs = pd.read_csv(f"data/{risk_level}_risk/rain_observed.csv", parse_dates=["timestamp"])
    rain_fc = pd.read_csv(f"data/{risk_level}_risk/rain_forecast.csv", parse_dates=["timestamp"])

    # Merge on timestamp so we have everything in one table
    df = (
        soil
        .merge(rain_obs, on="timestamp", how="left")
        .merge(rain_fc, on="timestamp", how="left")
        .sort_values("timestamp")
    )

    # Compute 6-hour cumulative rainfall (6h = 24 samples at 15-min intervals)
    df["rain_6h"] = df["rain_mm"].rolling(window=24, min_periods=1).sum()

    return df


def run_pipeline(risk_level: Literal["low", "moderate", "high"] = "low"):
    data = load_timeseries(risk_level)
    results = []

    for _, row in data.iterrows():
        # 8 soil-moisture channels at this timestep
        raw_readings = {
            "north_sensor": row["north_sensor"],
            "south_sensor": row["south_sensor"],
            "east_sensor": row["east_sensor"],
            "west_sensor": row["west_sensor"],
        }

        #TODO: cleaned = QC_and_smooth(raw_readings)

        saturation = normalize_moisture(raw_readings)

        features = compute_features(
            saturation_values=saturation,
            rain_6h_prev=row["rain_6h"],
            rain_12h_forecast=row["forecast_12h_mm"],
        )

        risk_score = compute_risk_score(features)
        category = map_risk_category(risk_score)
    
        results.append(
            {
                "timestamp": row["timestamp"],
                "raw_north": raw_readings["north_sensor"],
                "raw_south": raw_readings["south_sensor"],
                "raw_east": raw_readings["east_sensor"],
                "raw_west": raw_readings["west_sensor"],
                # save saturation values for inspection
                "sat_north": saturation["north_sensor"],
                "sat_south": saturation["south_sensor"],
                "sat_east": saturation["east_sensor"],
                "sat_west": saturation["west_sensor"],
                # save feature-level values
                "sat_avg": features["sat_avg"],
                "max_sat": features["max_sat"],
                "sat_asymmetry": features["sat_asymmetry"],
                "rain_6h_prev": features["rain_6h_prev"],
                "rain_12h_forecast": features["rain_12h_forecast"],
                # final outputs
                "risk_score": risk_score,
                "category": category,
            }
        )

    results_df = pd.DataFrame(results)
    results_df.to_csv(f"data/results/{risk_level}_risk_results.csv", index=False)
    print(f"Wrote results to data/results/{risk_level}_risk_results.csv")

def main():
    run_pipeline("low")
    run_pipeline("moderate")
    run_pipeline("high")

if __name__ == "__main__":
    main()