#!/usr/bin/env python3
"""
ft9_ascii_analyze_csv.py
------------------------

Analyze Log4OM CSV export (FT8/FT9 QSOs etc.) and print ASCII summaries:
 - Per-band summary (spots, uniques, median/mean/max distance)
 - Hourly histogram (UTC 00–23, cumulative, scaled bars)
 - Distance histogram (configurable bins)
 - Polar histogram (bearing distribution in 30° bins)

Author: (Your Name)
"""

import csv, os, math, configparser
from collections import defaultdict, Counter
from datetime import datetime

# --- Grid locator conversion ---
def maidenhead_to_latlon(locator):
    """Convert Maidenhead locator (4–6 chars) to approximate lat/lon (deg)."""
    locator = locator.strip().upper()
    if len(locator) < 4:
        return None
    lon = (ord(locator[0]) - ord('A')) * 20 - 180
    lat = (ord(locator[1]) - ord('A')) * 10 - 90
    lon += int(locator[2]) * 2
    lat += int(locator[3]) * 1
    if len(locator) >= 6:
        lon += (ord(locator[4]) - ord('A')) * 5/60
        lat += (ord(locator[5]) - ord('A')) * 2.5/60
    # Center of grid square
    return (lat + 0.5, lon + 1.0)

def haversine(lat1, lon1, lat2, lon2):
    """Calculate great-circle distance in km."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def bearing(lat1, lon1, lat2, lon2):
    """Calculate initial bearing (deg 0–360)."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dlambda = math.radians(lon2 - lon1)
    y = math.sin(dlambda) * math.cos(phi2)
    x = math.cos(phi1)*math.sin(phi2) - math.sin(phi1)*math.cos(phi2)*math.cos(dlambda)
    return (math.degrees(math.atan2(y, x)) + 360) % 360

def ascii_bar(val, maxval, width=40):
    """Draw scaled ASCII bar with '█' characters."""
    if maxval <= 0:
        return ""
    n = int(width * val / maxval)
    return "█" * n

# --- Main ---
def main():
    # Read config
    cfg = configparser.ConfigParser()
    cfg.read("config.ini")
    own = cfg["DEFAULT"].get("own_locator", "KP00aa")
    infile = cfg["DEFAULT"].get("input_file", "log.csv")
    infile = os.path.expanduser(infile)
    bin_km = cfg["DEFAULT"].getint("bin_km", 1000)
    show_hours = cfg["DEFAULT"].getboolean("show_hours", True)
    show_polar = cfg["DEFAULT"].getboolean("show_polar", True)

    own_latlon = maidenhead_to_latlon(own)

    # Parse CSV
    rows = []
    with open(infile, newline='', encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f, delimiter=";")
        for r in reader:
            call = r.get("call", "").strip()
            band = r.get("band", "").strip()
            dist = r.get("distance", "").replace(",", ".")
            dist = float(dist) if dist else None
            grid = r.get("gridsquare", "").strip().upper()
            date = r.get("qso_date", "")
            time = r.get("time_on", "")
            ts = None
            if date and time:
                try:
                    ts = datetime.strptime(date + time, "%Y%m%d%H%M%S")
                except:
                    pass
            latlon = None
            if grid:
                latlon = maidenhead_to_latlon(grid)
                if dist is None and own_latlon and latlon:
                    dist = haversine(*own_latlon, *latlon)
            rows.append({"call": call, "band": band, "dist": dist,
                         "grid": grid, "ts": ts, "latlon": latlon})

    # --- Per-band summary ---
    print("Per-band summary:")
    print(f"{'Band':<6}{'Spots':>7}{'Unique':>8}{'Median':>10}{'Mean':>10}{'Max':>10}")
    print("-"*60)
    by_band = defaultdict(list)
    for r in rows:
        if r["dist"]:
            by_band[r["band"]].append(r)
    for b in sorted(by_band.keys()):
        dists = [r["dist"] for r in by_band[b] if r["dist"]]
        if not dists:
            continue
        dists.sort()
        n = len(dists)
        med = dists[n//2] if n % 2 else (dists[n//2 - 1] + dists[n//2]) / 2
        mean = sum(dists) / n
        mx = max(dists)
        unique = len(set(r["call"] for r in by_band[b]))
        print(f"{b:<6}{n:7d}{unique:8d}{med:10.1f}{mean:10.1f}{mx:10.1f}")

    # --- Hourly histogram cumulative ---
    if show_hours:
        by_hour = defaultdict(list)
        for r in rows:
            if r["ts"] and r["dist"]:
                by_hour[r["ts"].hour].append(r["dist"])
        stats = []
        for h in range(24):
            vals = sorted(by_hour.get(h, []))
            n = len(vals)
            if n:
                med = vals[n//2] if n % 2 else (vals[n//2 - 1] + vals[n//2]) / 2
                mx = max(vals)
            else:
                med, mx = 0, 0
            stats.append((h, n, med, mx))
        max_spots = max(n for (_, n, _, _) in stats) or 1
        print("\nHourly histogram (UTC cumulative):")
        print("Hour   Spots   Median(km)   Max(km)  | Bar")
        print("-"*80)
        for (h, n, med, mx) in stats:
            bar = ascii_bar(n, max_spots, width=40)
            print(f"{h:02d}:00  {n:6d}   {med:9.1f}   {mx:7.0f}  | {bar}")

    # --- Distance histogram per band ---
    print(f"\nDistance histogram per band (bin={bin_km} km):")
    for b in sorted(by_band.keys()):
        dists = [r["dist"] for r in by_band[b] if r["dist"]]
        if not dists:
            continue
        bins = defaultdict(int)
        for d in dists:
            bb = int(d // bin_km) * bin_km
            bins[bb] += 1
        maxval = max(bins.values())
        print(f"\nBand {b}:")
        for bb in sorted(bins.keys()):
            n = bins[bb]
            bar = ascii_bar(n, maxval, width=40)
            print(f"{bb:5d}-{bb+bin_km-1:5d} km | {bar} {n}")


    # --- Polar histogram ---
    if show_polar and own_latlon:
        by_dir = Counter()
        for r in rows:
            if r["latlon"]:
                br = int(bearing(*own_latlon, *r["latlon"]) / 30) * 30
                by_dir[br] += 1
        if by_dir:
            print("\nASCII polar histogram (30° bins):")
            maxval = max(by_dir.values())
            for ang in range(0, 360, 30):
                n = by_dir.get(ang, 0)
                bar = ascii_bar(n, maxval, width=20)
                print(f"{ang:3d}°–{(ang+30)%360:3d}° | {bar} {n}")

if __name__ == "__main__":
    main()
