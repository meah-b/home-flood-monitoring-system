import openmeteo_requests
import pandas as pd


def get_24h_precip(lat: float, lon: float):
    """
    Fetch the next 24 hours of precipitation from the Open-Meteo GEM model.

    Returns:
        total_24h (float): total precip sum in mm
    """

    # Use built-in session (avoids ALL type-checker issues)
    openmeteo = openmeteo_requests.Client()

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "precipitation",
        "models": "gem_seamless",          # <- Uses the Canadian GEM model
        "forecast_days": 2,                # Enough hours to isolate "next 24h"
        "timezone": "America/Toronto"
    }

    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]

    hourly = response.Hourly()
    if hourly is None:
        raise RuntimeError("Hourly data missing in Open-Meteo response")
    
    var0 = hourly.Variables(0)
    if var0 is None:
        raise RuntimeError("Precipitation variable missing from hourly data")


    # Variable index matches order in "hourly" param
    precip = var0.ValuesAsNumpy()

    # Construct hourly timestamps using metadata
    times = pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s"),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s"),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    )

    df = pd.DataFrame({
        "timestamp": times,
        "precip_mm": precip
    })

    # Extract EXACT next 24 hours from the first forecast hour
    t0 = df["timestamp"].iloc[0]
    t24 = t0 + pd.Timedelta(hours=24)

    df_24h = df[(df["timestamp"] >= t0) & (df["timestamp"] < t24)]
    total_24h = float(df_24h["precip_mm"].sum())

    return round(total_24h, 2)
