import pandas as pd
from pythermalcomfort.models import utci
from config import ZONES, DATA_DIR
import os

def calculate_utci(row):
    # UTCI inputs: tdb (dry bulb temp), tr (mean radiant temp), v (wind speed), rh (relative humidity)
    tdb = row['corrected_temp']
    # Approximate tr (Mean Radiant Temperature) by adding a small factor based on solar radiation
    tr = tdb + (row['forecast_solar'] * 0.01) 
    
    # Wind speed in m/s at 10m height. UTCI expects wind speed at 10m.
    v = row['forecast_wind']
    rh = row['forecast_rh']
    
    try:
        result = utci(tdb=tdb, tr=tr, v=v, rh=rh)
        return result.utci
    except Exception as e:
        return tdb # fallback to dry bulb if out of bounds

def run_alerts():
    print("Loading inference results...")
    results_path = os.path.join(DATA_DIR, "inference_results.csv")
    df = pd.read_csv(results_path)
    
    print("Calculating UTCI for each hour...")
    df['utci'] = df.apply(calculate_utci, axis=1)
    
    # Analyze upcoming 5 days for severe heat alerts
    print("\n" + "="*50)
    print("DYNAMIC SPATIAL HEAT ALERTS (NCR)")
    print("="*50)
    
    # We define a base UTCI threshold for an extreme heat alert (e.g. 38 C UTCI = Very strong heat stress)
    BASE_ALERT_THRESHOLD = 38.0
    
    for zone in ZONES.keys():
        print(f"\nAnalyzing {zone}")
        
        # Filter for this zone
        zone_df = df[df['zone_name'] == zone]
        
        # Find peak risk times
        alerts = zone_df[zone_df['utci'] > BASE_ALERT_THRESHOLD]
        
        if alerts.empty:
            print("  -> No extreme heat alerts for the upcoming 5 days.")
        else:
            print(f"  -> {len(alerts)} hours of critical heat stress predicted!")
            # Show the top 3 most severe hours
            top_alerts = alerts.sort_values('utci', ascending=False).head(3)
            for _, row in top_alerts.iterrows():
                date_str = pd.to_datetime(row['date']).strftime('%Y-%m-%d %H:00')
                print(f"     [ALERT] {date_str} | UTCI: {row['utci']:.1f}°C (Threshold: {BASE_ALERT_THRESHOLD})")
                
    # Save the dataframe with the UTCI column
    df.to_csv(results_path, index=False)

if __name__ == "__main__":
    run_alerts()
