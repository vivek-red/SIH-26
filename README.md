# Microclimate Heat Alert System (Delhi-NCR)

This project is a dynamic, localized early warning system that predicts human thermal stress and microclimate heat risks for 15 zones across the Delhi-NCR region.

## Overview
Standard meteorological warnings often rely solely on ambient dry-bulb temperature, which fails to capture the compounding effects of relative humidity, wind speed, and solar radiation on the human body. This system aims to provide hyper-local, impact-based forecasting.

### Pipeline Architecture

1. **Data Ingestion (`data_ingestion.py`)**: Fetches historical hourly weather data (temperature, humidity, radiation, wind) from the Open-Meteo Archive API.
2. **Preprocessing (`preprocessing.py`)**: Computes time-based features (diurnal sine/cosine) and spatial features (lagged temperature) for machine learning.
3. **Model Training (`train_model.py`)**: Trains an XGBoost Regressor to predict the microclimate bias (Delta T) for temperature, achieving a highly accurate Mean Absolute Error (MAE).
4. **Real-Time Inference (`inference.py`)**: Fetches live 5-day forecasts, applies the XGBoost model to correct the forecast based on microclimate bias.
5. **Alert Layer & UTCI (`alert_layer.py`)**: Computes the Universal Thermal Climate Index (UTCI) using `pythermalcomfort` to assess human physiological heat stress.
6. **Streamlit App (`app.py`)**: A web interface rendering a Folium choropleth map with interactive polygons to visualize the risk levels across different zones.

## File Structure

```
microclimate_system/
├── data/                    # Generated datasets (ingested, preprocessed, inference, boundaries)
├── models/                  # Trained model weights and accuracy plots
├── scripts/                 # Utility scripts (boundary fetching, config generation)
├── app.py                   # Streamlit web application
├── config.py                # Centralized configuration and path definitions
├── data_ingestion.py        # Module 1
├── preprocessing.py         # Module 2
├── train_model.py           # Module 3
├── inference.py             # Module 4
├── alert_layer.py           # Module 5
├── main.py                  # End-to-end pipeline runner
└── requirements.txt         # Dependencies
```

## How to Run

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Data Pipeline (Optional, to retrain model or fetch fresh data):**
   ```bash
   python main.py
   ```

3. **Run the Application:**
   ```bash
   streamlit run app.py
   ```
