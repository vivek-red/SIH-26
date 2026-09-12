import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import time
from config import ZONES, DATA_DIR
import os

DATA_FILE = os.path.join(DATA_DIR, "ingested_data.csv")

# 3 Months of Historical Data (Offset by 7 days since ERA5 has a 5-day delay)
END_DATE = datetime.now() - timedelta(days=7)
START_DATE = END_DATE - timedelta(days=90)
START_STR = START_DATE.strftime('%Y-%m-%d')
END_STR = END_DATE.strftime('%Y-%m-%d')

def fetch_zone_data(zone_name, lat, lon):
    print(f"Fetching historical data for {zone_name} (Lat: {lat}, Lon: {lon})...")
    # 1. Fetch Actual Historical Data (ERA5)
    actual_url = (
        f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}"
        f"&start_date={START_STR}&end_date={END_STR}"
        f"&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m,shortwave_radiation"
        f"&timezone=auto"
    )
    
    try:
        response = requests.get(actual_url, timeout=15)
        response.raise_for_status()
        actual_data = response.json()
    except Exception as e:
        print(f"Error fetching actual historical data for {zone_name}: {e}")
        return None

    # 2. Fetch Historical Forecast Data (gfs_seamless)
    forecast_url = (
        f"https://historical-forecast-api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        f"&start_date={START_STR}&end_date={END_STR}"
        f"&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m,shortwave_radiation"
        f"&models=gfs_seamless"
        f"&timezone=auto"
    )

    try:
        response = requests.get(forecast_url, timeout=15)
        response.raise_for_status()
        forecast_data = response.json()
    except Exception as e:
        print(f"Error fetching historical forecast data for {zone_name}: {e}")
        return None

    # Process and merge
    if "hourly" in actual_data and "hourly" in forecast_data:
        df_actual = pd.DataFrame(actual_data["hourly"])
        df_actual = df_actual.rename(columns={
            "temperature_2m": "actual_temp",
            "relative_humidity_2m": "actual_rh",
            "wind_speed_10m": "actual_wind",
            "shortwave_radiation": "actual_solar"
        })
        df_actual["actual_temp"] = df_actual["actual_temp"].astype(float)

        df_forecast = pd.DataFrame(forecast_data["hourly"])
        df_forecast = df_forecast.rename(columns={
            "temperature_2m": "forecast_temp",
            "relative_humidity_2m": "forecast_rh",
            "wind_speed_10m": "forecast_wind",
            "shortwave_radiation": "forecast_solar"
        })

        # Merge on time
        df_merged = pd.merge(df_actual, df_forecast, on="time", how="inner")
        
        # Rename time to date to match preprocessing
        df_merged = df_merged.rename(columns={"time": "date"})
        
        # Add spatial features
        df_merged["zone_name"] = zone_name
        df_merged["lat"] = lat
        df_merged["lon"] = lon
        
        # Drop rows with missing values (since GFS seamless can have gaps)
        df_merged.dropna(inplace=True)
        return df_merged
    return None

def main():
    all_dfs = []
    for zone, coords in ZONES.items():
        df_zone = fetch_zone_data(zone, coords["lat"], coords["lon"])
        if df_zone is not None:
            all_dfs.append(df_zone)
        # Sleep slightly to respect free API rate limits
        time.sleep(1)
        
    if all_dfs:
        final_df = pd.concat(all_dfs, ignore_index=True)
        final_df.to_csv(DATA_FILE, index=False)
        print(f"Data ingestion complete. Combined {len(all_dfs)} zones into {len(final_df)} rows at {DATA_FILE}")
    else:
        print("Failed to ingest any data.")

if __name__ == "__main__":
    main()
