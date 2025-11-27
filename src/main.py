from src.quality_control import QC_and_smooth
from src.normalization import normalize_moisture
from src.features import compute_features
from src.risk_model import compute_risk_score, map_risk_category

import pandas as pd

def run_pipeline():
    #TODO: fetch batch of data from Firebase: batch_readings, previous_valid_reading, soil_saturation_1h_ago, lat, lon, soil_type
    data = pd.read_csv(f"data/test_data/current_soil_moisture.csv", parse_dates=["timestamp"]) # Placeholder for Firebase fetch
    results = []
    batch_readings = []

    for _, row in data.iterrows():
        # 4 soil-moisture channels at this timestep
        batch_readings.append(
            {
                "north_sensor": row["north_sensor"],
                "south_sensor": row["south_sensor"],
                "east_sensor": row["east_sensor"],
                "west_sensor": row["west_sensor"],
            }
        )

    previous_valid_reading = None  # TODO: replace this with a real batch fetch from Firebase

    cleaned_readings = QC_and_smooth(
        batch_readings,
        previous_valid_reading,
    )
    
    #TODO: replace these with the fetch from Firebase
    soil_saturation_1h_ago = 0.5 
    lat = 42.9973110477211
    lon = -81.3101143606061
    soil_type="clay_loam"

    saturation = normalize_moisture(cleaned_readings, soil_type)
    features = compute_features(
        saturation,
        soil_saturation_1h_ago,
        lat,
        lon
    )

    risk_score_internal, risk_score_displayed, base_soil_risk, storm_factor, site_sensitivity_factor = compute_risk_score(features["sat_avg"],
                                    features["soil_saturation_1h_ago"],
                                    features["forecast_24h_mm"],
                                    features["IDF_24h_2yr_mm"])
    
    #TODO: save risk_score_internal to Firebase (and other intermediate values if desired)
    
    category = map_risk_category(risk_score_displayed)

    results.append(
        {
            "raw_north": cleaned_readings["north_sensor"],
            "raw_south": cleaned_readings["south_sensor"],
            "raw_east": cleaned_readings["east_sensor"],
            "raw_west": cleaned_readings["west_sensor"],
            "sat_north": saturation["north_sensor"],
            "sat_south": saturation["south_sensor"],
            "sat_east": saturation["east_sensor"],
            "sat_west": saturation["west_sensor"],
            "sat_avg": features["sat_avg"],
            "asymmetry": features["asymmetry"],
            "forecast_24h_mm": features["forecast_24h_mm"],
            "IDF_24h_2yr_mm": features["IDF_24h_2yr_mm"],
            "base_soil_risk": base_soil_risk,
            "storm_factor": storm_factor,
            "site_sensitivity_factor": site_sensitivity_factor,
            "risk_score_internal": risk_score_internal,
            "risk_score": risk_score_displayed,
            "category": category,
        }
    )

    results_df = pd.DataFrame(results)
    results_df.to_csv(f"data/results/risk_results.csv", index=False)
    print(f"Wrote results to data/results/risk_results.csv")

def main():
    run_pipeline()

if __name__ == "__main__":
    main()