import json
import sys
import os
import osmnx as ox

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

queries = {
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

print("ZONES = {")
for name, q in queries.items():
    try:
        gdf = ox.geocode_to_gdf(q)
        centroid = gdf.geometry.centroid.iloc[0]
        lat, lon = centroid.y, centroid.x
        print(f'    "{name}": {{"lat": {lat:.4f}, "lon": {lon:.4f}}},')
    except Exception as e:
        print(f'    # FAILED: "{name}"')
print("}")
