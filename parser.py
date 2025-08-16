import math, csv, io
from collections import defaultdict, Counter
from datetime import datetime

def maidenhead_to_latlon(locator):
    locator = locator.strip().upper()
    if len(locator) < 4:
        return None
    lon = (ord(locator[0]) - ord('A')) * 20 - 180
    lat = (ord(locator[1]) - ord('A')) * 10 - 90
    lon += int(locator[2]) * 2
    lat += int(locator[3]) * 1
    return (lat + 0.5, lon + 1.0)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def analyze(text, own_locator, bin_km, show_hours, show_polar):
    """Parse Log4OM CSV, compute stats, return JSON."""
    own_latlon = maidenhead_to_latlon(own_locator)

    reader = csv.DictReader(io.StringIO(text), delimiter=";")
    rows = []
    for r in reader:
        grid = r.get("gridsquare", "")
        dist = r.get("distance", "")
        dist = float(dist.replace(",", ".")) if dist else None
        if grid and own_latlon and not dist:
            loc = maidenhead_to_latlon(grid)
            if loc:
                dist = haversine(*own_latlon, *loc)
        if dist:
            rows.append({"band": r.get("band",""), "dist": dist})

    # Group per band
    by_band = defaultdict(list)
    for r in rows:
        by_band[r["band"]].append(r["dist"])

    band_summary = []
    for b, dists in by_band.items():
        if not dists: continue
        dists.sort()
        n = len(dists)
        med = dists[n//2]
        mean = sum(dists)/n
        mx = max(dists)
        band_summary.append({
            "band": b, "spots": n,
            "median": round(med,1),
            "mean": round(mean,1),
            "max": round(mx,1)
        })

    # Distance histogram per band
    histograms = {}
    for b, dists in by_band.items():
        bins = defaultdict(int)
        for d in dists:
            bb = int(d // bin_km) * bin_km
            bins[bb] += 1
        histograms[b] = dict(sorted(bins.items()))

    return {"summary": band_summary, "histograms": histograms}
