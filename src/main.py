from quality_control import QC_and_smooth
from src.normalization import normalize_moisture
from src.features import compute_features
from src.risk_model import compute_risk_score, map_risk_category

import pandas as pd

def run_pipeline():
    #TODO: fetch batch of data from Firebase: batch_readings, previous_valid_reading, soil_saturation_1h_ago
    data = pd.read_csv(f"data/moderate_risk/soil_moisture_timeseries.csv", parse_dates=["timestamp"]) # Placeholder for Firebase fetch
    results = []

    for _, row in data.iterrows():
        # 4 soil-moisture channels at this timestep
        raw_readings = {
            "north_sensor": row["north_sensor"],
            "south_sensor": row["south_sensor"],
            "east_sensor": row["east_sensor"],
            "west_sensor": row["west_sensor"],
        }

        previous_valid_reading = None  # TODO: replace this with a real batch fetch from Firebase
        batch_readings = [raw_readings]

        cleaned_readings = QC_and_smooth(
            batch_readings=batch_readings,
            previous_valid_reading=previous_valid_reading,
        )
        saturation = normalize_moisture(cleaned_readings)
        soil_saturation_1h_ago = 0.5 #TODO: replace with fetch from firebase

        features = compute_features(
            saturation_values=saturation,
            soil_saturation_1h_ago=soil_saturation_1h_ago
        )

        risk_score_internal, risk_score_displayed = compute_risk_score(features["sat_avg"],
                                        features["soil_saturation_1h_ago"],
                                        features["forecast_24h_mm"],
                                        features["IDF_24h_2yr_mm"])
        
        #TODO: save risk_score_internal to Firebase (and other intermediate values if desired)
        
        category = map_risk_category(risk_score_displayed)
    
        results.append(
            {
                "timestamp": row["timestamp"],
                "raw_north": raw_readings["north_sensor"],
                "raw_south": raw_readings["south_sensor"],
                "raw_east": raw_readings["east_sensor"],
                "raw_west": raw_readings["west_sensor"],
                "sat_north": saturation["north_sensor"],
                "sat_south": saturation["south_sensor"],
                "sat_east": saturation["east_sensor"],
                "sat_west": saturation["west_sensor"],
                "sat_avg": features["sat_avg"],
                "max_sat": features["max_sat"],
                "sat_asymmetry": features["sat_asymmetry"],
                "rain_6h_prev": features["rain_6h_prev"],
                "rain_12h_forecast": features["rain_12h_forecast"],
                "risk_score": risk_score_displayed,
                "category": category,
            }
        )

    results_df = pd.DataFrame(results)
    results_df.to_csv(f"data/results/moderate_risk_results.csv", index=False)
    print(f"Wrote results to data/results/moderate_risk_results.csv")

def main():
    run_pipeline()

if __name__ == "__main__":
    main()