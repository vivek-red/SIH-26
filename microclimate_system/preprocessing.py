import pandas as pd
import numpy as np
import os
from config import DATA_DIR

def preprocess_data(input_csv=os.path.join(DATA_DIR, "ingested_data.csv"), output_csv=os.path.join(DATA_DIR, "preprocessed_data.csv")):
    print(f"Loading data from {input_csv}...")
    df = pd.read_csv(input_csv)
    df['date'] = pd.to_datetime(df['date'])
    
    # Target Variable: ΔT
    df['delta_T'] = df['actual_temp'] - df['forecast_temp']
    
    # Feature: Diurnal Sine/Cosine
    df['hour'] = df['date'].dt.hour
    df['diurnal_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['diurnal_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    
    # Feature: 24h Thermal Lag
    # We want to know what the temperature was exactly 24 hours ago.
    # We will use the forecast temperature as the base feature (since at inference, we only have past forecasts/actuals, 
    # but practically we can just use the past 24h actual temperature if it's a rolling system.
    # Feature 2: 24h Thermal Lag (temperature 24 hours ago)
    # We must group by zone_name so the shift doesn't bleed temperatures across cities
    df = df.sort_values(['zone_name', 'date'])
    df["temp_lag_24h"] = df.groupby("zone_name")["forecast_temp"].shift(24)
    
    # Drop rows with NaN from the lag shift
    df = df.dropna()
    
    print(f"Features generated. Saving to {output_csv}...")
    df.to_csv(output_csv, index=False)
    return df

if __name__ == "__main__":
    preprocess_data()
