import pandas as pd
import requests

EM_BASE_URL = "https://api.electricitymaps.com/v4"

def fetch_intensity(zone, start, end, token):
    """Hourly carbon intensity (gCO2eq/kWh) for a given zone and time range."""
    r = requests.get(
        f"{EM_BASE_URL}/carbon-intensity/past-range",
        params={"zone": zone, "start": start, "end": end, "emissionFactorType": "lifecycle"},
        headers={"auth-token": token},
        timeout=30,
    )
    r.raise_for_status()
    df = pd.DataFrame(r.json()["data"])
    return df.set_index(pd.to_datetime(df["datetime"]))["carbonIntensity"]

class IntensitySeries:
    """Replays a cached hourly carbon intensity series for a given zone and time range."""

    def __init__(self, csv_path, queries_per_hour, start_hour=0):
        self.ci = pd.read_csv(csv_path, index_col=0, parse_dates=True).iloc[:, 0].to_numpy()
        self.queries_per_hour = queries_per_hour
        self.start_hour = start_hour

    def at_step(self, t):
        h = self.start_hour + t // self.queries_per_hour
        if h >= len(self.ci):
            raise IndexError(f"Step {t} needs hour {h}, but series has {len(self.ci)} hours")
        return self.ci[h]
    
def global_ci_bounds(series_list):
    """Min/max intensity across every zone being compared."""
    return min(s.ci.min() for s in series_list), max(s.ci.max() for s in series_list)