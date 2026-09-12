import osmnx as ox

queries = [
    "New Delhi, Delhi, India",
    "North Delhi, Delhi, India",
    "South Delhi, Delhi, India",
    "East Delhi, Delhi, India",
    "West Delhi, Delhi, India",
    "North East Delhi, Delhi, India",
    "North West Delhi, Delhi, India",
    "Shahdara, Delhi, India",
    "South East Delhi, Delhi, India",
    "South West Delhi, Delhi, India"
]

for q in queries:
    try:
        gdf = ox.geocode_to_gdf(q)
        print(f"SUCCESS: {q}")
    except Exception as e:
        print(f"FAILED: {q} - {e}")
