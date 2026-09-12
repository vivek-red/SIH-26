import osmnx as ox
import geopandas as gpd
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ZONES, DATA_DIR
import json

# Add osm queries to ZONES for fetching polygons
# The more specific, the better for Nominatim API
osm_queries = {
    "Central Delhi": "Central Delhi, Delhi, India",
    "Gurugram": "Gurugram, Haryana, India",
    "Noida": "Gautam Buddha Nagar, Uttar Pradesh, India",
    "Faridabad": "Faridabad District, Haryana, India",
    "Ghaziabad": "Ghaziabad District, Uttar Pradesh, India",
    "New Delhi": "New Delhi, Delhi, India",
    "North Delhi": "North Delhi, Delhi, India",
    "South Delhi": "South Delhi, Delhi, India",
    "East Delhi": "East Delhi, Delhi, India",
    "West Delhi": "West Delhi, Delhi, India",
    "North East Delhi": "North East Delhi, Delhi, India",
    "North West Delhi": "North West Delhi, Delhi, India",
    "Shahdara": "Shahdara, Delhi, India",
    "South East Delhi": "South East Delhi, Delhi, India",
    "South West Delhi": "South West Delhi, Delhi, India"
}
def fetch_and_save():
    print("Fetching boundaries from OpenStreetMap via OSMnx...")
    gdfs = []
    for zone, query in osm_queries.items():
        print(f"  Fetching: {query}")
        try:
            # geocode_to_gdf returns a GeoDataFrame with the polygon
            gdf = ox.geocode_to_gdf(query)
            # Standardize identifying column
            gdf = gdf[['geometry']].copy()
            gdf['zone_name'] = zone
            gdfs.append(gdf)
        except Exception as e:
            print(f"  Failed for {zone}: {e}")
            
    if not gdfs:
        print("No boundaries fetched.")
        return
        
    final_gdf = pd.concat(gdfs, ignore_index=True)
    
    # Save to GeoJSON
    out_file = os.path.join(DATA_DIR, "ncr_zones.geojson")
    final_gdf.to_file(out_file, driver="GeoJSON")
    print(f"Successfully saved {len(final_gdf)} boundaries to {out_file}")

if __name__ == "__main__":
    fetch_and_save()
