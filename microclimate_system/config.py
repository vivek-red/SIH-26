import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")

ZONES = {
    "Central Delhi": {"lat": 28.6437, "lon": 77.1648},
    "Gurugram": {"lat": 28.3688, "lon": 76.9408},
    "Noida": {"lat": 28.3951, "lon": 77.5549},
    "Faridabad": {"lat": 28.3521, "lon": 77.3427},
    "Ghaziabad": {"lat": 28.7687, "lon": 77.4766},
    "New Delhi": {"lat": 28.6041, "lon": 77.2046},
    "North Delhi": {"lat": 28.7445, "lon": 77.1882},
    "South Delhi": {"lat": 28.4923, "lon": 77.1845},
    "East Delhi": {"lat": 28.6294, "lon": 77.2920},
    "West Delhi": {"lat": 28.6381, "lon": 77.0752},
    "North East Delhi": {"lat": 28.7044, "lon": 77.2722},
    "North West Delhi": {"lat": 28.7061, "lon": 77.0901},
    "Shahdara": {"lat": 28.6698, "lon": 77.2922},
    "South East Delhi": {"lat": 28.5460, "lon": 77.2739},
    "South West Delhi": {"lat": 28.5742, "lon": 76.9776},
}
