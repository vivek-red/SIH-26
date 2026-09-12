import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os
import subprocess
import sys
from config import ZONES, DATA_DIR, MODELS_DIR

# Configure page
st.set_page_config(page_title="Microclimate Heat Alerts", layout="wide")

st.title("🌡️ Spatial Microclimate Heat Alert System (NCR)")
st.markdown("Monitor urban heat island (UHI) effects and dynamic physiological heat stress across 5 geographic zones in the National Capital Region (NCR).")

# Sidebar for controls
with st.sidebar:
    st.header("Pipeline Controls")
    if st.button("🔄 Run Full Pipeline"):
        with st.spinner("Executing data ingestion, model training, and inference across all 5 zones..."):
            try:
                py_exec = sys.executable
                subprocess.run([py_exec, "main.py"], check=True)
                st.success("Pipeline executed successfully!")
            except Exception as e:
                st.error(f"Pipeline failed: {e}")
                
    st.markdown("---")
    st.markdown("**About**\n\nThis system uses hyper-local Open-Meteo GFS forecasts corrected by an XGBoost model trained on historical ERA5 ground-truth to predict physiological heat stress (UTCI) uniquely for each distinct zone.")

BASE_ALERT_THRESHOLD = 38.0 # UTCI threshold for severe heat stress

# Load data if available
inference_file = os.path.join(DATA_DIR, "inference_results.csv")
if os.path.exists(inference_file):
    df = pd.read_csv(inference_file)
    
    # Calculate UTCI if not already done
    if 'utci' not in df.columns:
        from pythermalcomfort.models import utci
        def calculate_utci(row):
            tdb = row['corrected_temp']
            tr = tdb + (row['forecast_solar'] * 0.01) 
            v = row['forecast_wind']
            rh = row['forecast_rh']
            try:
                result = utci(tdb=tdb, tr=tr, v=v, rh=rh)
                return result.utci
            except:
                return tdb
        df['utci'] = df.apply(calculate_utci, axis=1)
        
    # Calculate max risk per zone
    zone_risks = {}
    for zone in ZONES.keys():
        zone_df = df[df['zone_name'] == zone]
        if not zone_df.empty:
            max_risk = zone_df['utci'].max()
            zone_risks[zone] = max_risk
        else:
            zone_risks[zone] = 0
            
    # Map color logic
    def get_color_and_status(risk):
        if risk > BASE_ALERT_THRESHOLD + 5:
            return "darkred", "Extreme Danger", "Dispatch emergency SMS, open 24/7 cooling centers, halt outdoor labor."
        elif risk > BASE_ALERT_THRESHOLD:
            return "red", "Critical Heat", "Activate cooling centers, issue public warnings, avoid direct sun."
        elif risk > BASE_ALERT_THRESHOLD - 5:
            return "orange", "Moderate Risk", "Stay hydrated, limit outdoor activities during peak hours."
        else:
            return "green", "Safe", "Normal hydration, no immediate action required."

    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🗺️ NCR Spatial Risk Map (5-Day Peak)")
        # Create Folium Map centered on NCR
        m = folium.Map(location=[28.5355, 77.2090], zoom_start=10)
        
        # Add GeoJSON boundaries if available
        geojson_path = os.path.join(DATA_DIR, "ncr_zones.geojson")
        if os.path.exists(geojson_path):
            def style_function(feature):
                zone = feature['properties']['zone_name']
                max_risk = zone_risks.get(zone, 0)
                color, _, _ = get_color_and_status(max_risk)
                return {
                    'fillColor': color,
                    'color': 'black',
                    'weight': 2,
                    'fillOpacity': 0.6
                }
            
            folium.GeoJson(
                geojson_path,
                name="NCR Zones",
                style_function=style_function,
                tooltip=folium.GeoJsonTooltip(fields=['zone_name'], aliases=['Zone:'])
            ).add_to(m)
        else:
            # Fallback to markers if geojson not generated yet
            for zone, info in ZONES.items():
                max_risk = zone_risks[zone]
                color, status, action = get_color_and_status(max_risk)
                folium.CircleMarker(
                    location=[info["lat"], info["lon"]],
                    radius=15,
                    popup=f"<b>{zone}</b><br>Peak Risk: {max_risk:.1f}°C UTCI<br>Status: {status}",
                    tooltip=zone,
                    color=color,
                    fill=True,
                    fill_color=color,
                    fillOpacity=0.7
                ).add_to(m)
            
        st_folium(m, width=700, height=500)
        
    with col2:
        st.subheader("⚠️ Actionable Steps")
        for zone, info in ZONES.items():
            max_risk = zone_risks[zone]
            color, status, action = get_color_and_status(max_risk)
            
            # Use streamlit info/warning/error boxes based on color
            if color in ["red", "darkred"]:
                st.error(f"**{zone}**\n\n{action}")
            elif color == "orange":
                st.warning(f"**{zone}**\n\n{action}")
            else:
                st.success(f"**{zone}**\n\n{action}")
                
    st.markdown("---")
    
    st.subheader("📊 Forecast Data & Model Accuracy")
    tab1, tab2 = st.tabs(["Raw Inference Data", "Model Evaluation"])
    
    with tab1:
        st.dataframe(df[['zone_name', 'date', 'forecast_temp', 'corrected_temp', 'utci']])
        
    with tab2:
        plot_path = os.path.join(MODELS_DIR, "test_accuracy.png")
        if os.path.exists(plot_path):
            st.image(plot_path, caption="XGBoost Predicted Bias vs Actuals")
        else:
            st.info("Test accuracy plot not found. Run the pipeline to generate it.")
else:
    st.warning("No inference data found. Please run the pipeline from the sidebar.")
