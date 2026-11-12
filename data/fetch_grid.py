"""Download hourly carbon intensity for each zone in config/grid.yaml.

Writes data/grid/<zone>.csv (datetime, carbon_intensity) and data/grid/bounds.yaml with the
min/max across all zones, which CarbonNormalizer uses so every zone shares one scale.

From the API (needs ELECTRICITYMAPS_TOKEN; history beyond recent days may need a paid plan):
    python data/fetch_grid.py
    python data/fetch_grid.py --zones DE FR

From Electricity Maps' downloadable hourly datasets (one CSV per zone and year):
    python data/fetch_grid.py --from-csv DE=~/Downloads/DE_2025_hourly.csv FR=~/Downloads/FR_2025_hourly.csv
"""
import argparse
import os
import sys

import pandas as pd
import yaml

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.manager import load_config
from src.metrics.grid import fetch_intensity

GRID_DIR = "data/grid"
MAX_GAP_HOURS = 6  # interpolate shorter gaps; longer ones mean the download is incomplete


def fetch_zone(zone, start, end, token, chunk_days):
    """Fetch [start, end) in chunks, since past-range caps how much one request returns."""
    parts = []
    chunk_start = start
    while chunk_start < end:
        chunk_end = min(chunk_start + pd.Timedelta(days=chunk_days), end)
        parts.append(
            fetch_intensity(zone, chunk_start.isoformat(), chunk_end.isoformat(), token)
        )
        chunk_start = chunk_end
    return pd.concat(parts)


def read_portal_csv(path, emission_factor):
    """Read an Electricity Maps hourly dataset CSV and return the chosen intensity column."""
    df = pd.read_csv(os.path.expanduser(path))
    time_col = next(c for c in df.columns if c.lower().startswith("datetime"))
    wanted = "life cycle" if emission_factor == "lifecycle" else "direct"
    ci_cols = [c for c in df.columns if "carbon intensity" in c.lower() and wanted in c.lower()]
    if not ci_cols:
        raise ValueError(f"{path}: no '{wanted}' carbon intensity column in {list(df.columns)}")
    return df.set_index(pd.to_datetime(df[time_col], utc=True))[ci_cols[0]]


def clean(series, zone, start, end):
    """One value per hour over [start, end); short gaps interpolated, long gaps rejected."""
    series = series[~series.index.duplicated(keep="last")].sort_index()
    hours = pd.date_range(start, end, freq="h", inclusive="left")
    series = series.reindex(hours)
    missing = series.isna()
    if missing.any():
        longest = missing.astype(int).groupby((~missing).cumsum()).sum().max()
        if longest > MAX_GAP_HOURS:
            raise ValueError(f"{zone}: {missing.sum()} hours missing, longest gap {longest} h")
        print(f"  {zone}: interpolating {missing.sum()} missing hours")
        series = series.interpolate(limit_direction="both")
    series.index.name = "datetime"
    return series.rename("carbon_intensity")


def main():
    parser = argparse.ArgumentParser(description="Download grid carbon intensity per zone")
    parser.add_argument("--zones", nargs="*", help="Subset of zones in config/grid.yaml")
    parser.add_argument("--from-csv", nargs="*", metavar="ZONE=PATH",
                        help="Use downloaded Electricity Maps hourly CSVs instead of the API")
    args = parser.parse_args()

    config = load_config("grid")
    start = pd.Timestamp(config["period"]["start"])
    end = pd.Timestamp(config["period"]["end"])
    emission_factor = config.get("emission_factor", "lifecycle")
    os.makedirs(GRID_DIR, exist_ok=True)

    if args.from_csv:
        sources = dict(item.split("=", 1) for item in args.from_csv)
        for zone, path in sources.items():
            series = clean(read_portal_csv(path, emission_factor), zone, start, end)
            series.to_csv(os.path.join(GRID_DIR, f"{zone}.csv"))
            print(f"{zone}: {len(series)} hours from {path}")
    else:
        token = os.environ.get(config["api"]["token_env"])
        if not token:
            sys.exit(f"Set {config['api']['token_env']} (or use --from-csv).")
        if emission_factor != "lifecycle":
            sys.exit("fetch_intensity requests lifecycle factors; use --from-csv for direct.")
        for zone in args.zones or list(config["zones"]):
            print(f"Fetching {zone} ({start.date()} to {end.date()})...")
            raw = fetch_zone(zone, start, end, token, config["api"]["chunk_days"])
            series = clean(raw, zone, start, end)
            series.to_csv(os.path.join(GRID_DIR, f"{zone}.csv"))
            print(f"{zone}: {len(series)} hours, mean {series.mean():.0f} gCO2eq/kWh")

    # Global bounds over every zone in the config that has data, so all zones share one scale
    stats = {}
    for zone in config["zones"]:
        path = os.path.join(GRID_DIR, f"{zone}.csv")
        if os.path.exists(path) and os.path.getsize(path) > 0:
            ci = pd.read_csv(path, index_col=0)["carbon_intensity"]
            stats[zone] = {"min": float(ci.min()), "mean": float(ci.mean()), "max": float(ci.max())}
    if stats:
        bounds = {
            "ci_min": min(s["min"] for s in stats.values()),
            "ci_max": max(s["max"] for s in stats.values()),
            "emission_factor": emission_factor,
            "period": {"start": config["period"]["start"], "end": config["period"]["end"]},
            "zones": stats,
        }
        with open(os.path.join(GRID_DIR, "bounds.yaml"), "w") as f:
            yaml.safe_dump(bounds, f, sort_keys=False)
        print(f"Global bounds {bounds['ci_min']:.0f}-{bounds['ci_max']:.0f} gCO2eq/kWh "
              f"over {list(stats)} -> {GRID_DIR}/bounds.yaml")
        missing = [z for z in config["zones"] if z not in stats]
        if missing:
            print(f"Note: no data yet for {missing}; bounds will change once they're added")


if __name__ == "__main__":
    main()
