import pandas as pd
import numpy as np
import xgboost as xgb
import requests
from config import ZONES, DATA_DIR, MODELS_DIR
import os
import time

def fetch_live_forecast(zone_name, lat, lon):
    """Fetch 5-day live forecast with 1 day of past data for lag features"""
    print(f"Fetching live 5-day forecast for {zone_name}...")
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", "shortwave_radiation"],
        "past_days": 1,
        "forecast_days": 5,
        "timezone": "auto"
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error fetching forecast for {zone_name}: {e}")
        return None
        
    if "hourly" in data:
        hourly_data = data["hourly"]
        df = pd.DataFrame(hourly_data)
        df = df.rename(columns={
            "temperature_2m": "forecast_temp",
            "relative_humidity_2m": "forecast_rh",
            "wind_speed_10m": "forecast_wind",
            "shortwave_radiation": "forecast_solar",
            "time": "date"
        })
        df["date"] = pd.to_datetime(df["date"])
        df["zone_name"] = zone_name
        df["lat"] = lat
        df["lon"] = lon
        return df
    return None

def run_inference():
    all_dfs = []
    for zone, coords in ZONES.items():
        df_zone = fetch_live_forecast(zone, coords["lat"], coords["lon"])
        if df_zone is not None:
            all_dfs.append(df_zone)
        time.sleep(1)
        
    df = pd.concat(all_dfs, ignore_index=True)
    
    # Feature Engineering for Inference
    df['hour'] = df['date'].dt.hour
    df['diurnal_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['diurnal_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    
    # Group by zone to calculate 24h lag
    df = df.sort_values(['zone_name', 'date'])
    df['temp_lag_24h'] = df.groupby('zone_name')['forecast_temp'].shift(24)
    
    # Drop the past_days data now that we have the lag
    df = df.dropna().reset_index(drop=True)
    
    # Load Model
    print("Loading XGBoost model...")
    model = xgb.XGBRegressor()
    model_path = os.path.join(MODELS_DIR, "xgboost_model.json")
    model.load_model(model_path)
    
    features = [
        'forecast_temp', 
        'forecast_rh', 
        'forecast_wind', 
        'forecast_solar',
        'diurnal_sin', 
        'diurnal_cos', 
        'temp_lag_24h',
        'lat',
        'lon'
    ]
    
    print("Predicting Microclimate Bias (Delta T)...")
    df['predicted_delta_T'] = model.predict(df[features])
    
    df['corrected_temp'] = df['forecast_temp'] + df['predicted_delta_T']
    
    results_path = os.path.join(DATA_DIR, "inference_results.csv")
    df.to_csv(results_path, index=False)
    print(f"Inference complete. Corrected forecasts saved to {results_path}")
    return df

if __name__ == "__main__":
    run_inference()
