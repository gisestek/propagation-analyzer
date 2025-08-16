# backend/parser.py
import csv, math, re
from collections import defaultdict

# ---------- helpers ----------
def maidenhead_to_latlon(locator: str):
    """Convert Maidenhead (e.g., KP26vl) to approx (lat, lon) degrees."""
    loc = (locator or "").strip().upper()
    if len(loc) < 4:
        raise ValueError("Locator too short")
    lon = (ord(loc[0]) - ord('A')) * 20 - 180
    lat = (ord(loc[1]) - ord('A')) * 10 - 90
    lon += int(loc[2]) * 2
    lat += int(loc[3]) * 1
    if len(loc) >= 6:
        lon += (ord(loc[4]) - ord('A')) * (5/60)
        lat += (ord(loc[5]) - ord('A')) * (2.5/60)
    # cell center
    return (lat + 0.5, lon + 1.0)

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def band_from_freq_mhz(freq_mhz: float) -> str:
    if 1.8 <= freq_mhz < 2.0: return "160m"
    if 3.5 <= freq_mhz < 4.0: return "80m"
    if 5.0 <= freq_mhz < 5.5: return "60m"
    if 7.0 <= freq_mhz < 7.3: return "40m"
    if 10.0 <= freq_mhz < 10.2: return "30m"
    if 14.0 <= freq_mhz < 14.35: return "20m"
    if 18.0 <= freq_mhz < 18.2: return "17m"
    if 21.0 <= freq_mhz < 21.45: return "15m"
    if 24.8 <= freq_mhz < 25.0: return "12m"
    if 28.0 <= freq_mhz < 29.7: return "10m"
    if 50.0 <= freq_mhz < 54.0: return "6m"
    if 70.0 <= freq_mhz < 71.0: return "4m"
    if 144.0 <= freq_mhz < 148.0: return "2m"
    if 432.0 <= freq_mhz < 438.0: return "70cm"
    return f"{freq_mhz:.3f} MHz"

TS_RE = re.compile(r"^\d{6}_\d{4,6}$")  # YYMMDD_HHMM or YYMMDD_HHMMSS
def looks_like_grid(tok: str) -> bool:
    t = (tok or "").upper()
    return len(t) in (4, 6) and t[:2].isalpha() and t[2:4].isdigit()

# ---------- CSV (Log4OM) streaming ----------
def analyze_csv_stream(text_stream, locator, bin_km=1000):
    """Stream-parse Log4OM CSV. Sniff delimiter, normalize headers, compute per-band + distance histograms."""
    my = maidenhead_to_latlon(locator)

    # sniff delimiter from first line
    pos = text_stream.tell()
    head = text_stream.readline()
    delim = ";" if ";" in head else ("," if "," in head else ";")
    text_stream.seek(pos)

    reader = csv.DictReader(text_stream, delimiter=delim)
    if not reader.fieldnames:
        return {"source":"Log4OM CSV","total_qsos":0,"bands":{},"distance_histogram":{},"distance_histograms_by_band":{}}
    norm_map = {fn: fn.strip().lower().replace(" ", "") for fn in reader.fieldnames}

    def get(row, *cands):
        for c in cands:
            for raw, norm in norm_map.items():
                if norm == c:
                    return row.get(raw, "")
        return ""

    total = 0
    per_band = defaultdict(int)
    dist_bins = defaultdict(int)
    dist_bins_by_band = defaultdict(lambda: defaultdict(int))
    grid_ll_cache, grid_dist_cache = {}, {}

    for row in reader:
        band = (get(row, "band") or "").strip()
        grid = (get(row, "gridsquare","grid","gridsq","grids") or "").strip().upper()

        # supplied distance?
        dist = None
        ds = (get(row,"distance") or "").replace(",", ".").strip()
        if ds:
            try: dist = float(ds)
            except ValueError: dist = None

        # else compute from grid
        if dist is None and len(grid) >= 4:
            dist = grid_dist_cache.get(grid)
            if dist is None:
                ll = grid_ll_cache.get(grid)
                if ll is None:
                    try: ll = maidenhead_to_latlon(grid)
                    except Exception: ll = None
                    grid_ll_cache[grid] = ll
                if ll:
                    dist = haversine_km(my[0], my[1], ll[0], ll[1])
                    grid_dist_cache[grid] = dist

        if band:
            per_band[band] += 1
        if dist:
            bucket = int(dist // bin_km) * bin_km
            dist_bins[bucket] += 1
            if band:
                dist_bins_by_band[band][bucket] += 1
            total += 1  # count usable rows

    return {
        "source": "Log4OM CSV",
        "total_qsos": total,
        "bands": dict(per_band),
        "distance_histogram": {str(k): v for k, v in sorted(dist_bins.items())},
        "distance_histograms_by_band": {
            b: {str(k): v for k, v in sorted(bins.items())}
            for b, bins in dist_bins_by_band.items()
        },
    }

# ---------- WSJT-X ALL.TXT (CQ) streaming ----------
def analyze_alltxt_stream(text_stream, own_locator: str, bin_km: int = 1000):
    """Robust streaming parser for WSJT-X ALL.TXT CQ spots.

    Accepts lines like:
      YYMMDD_HHMMSS  14074  -10  0.2  1234  CQ K1ABC FN20
      YYMMDD_HHMM    7074   -09  0.3  1200  CQ XX1XX AB12
    Logic:
      - ts = first token matches TS_RE
      - freq = second token (kHz or MHz) → band
      - require 'CQ' in tokens
      - grid = last token that looks like Maidenhead (4/6)
    """
    my = maidenhead_to_latlon(own_locator)

    per_band = defaultdict(int)
    dist_bins = defaultdict(int)
    dist_bins_by_band = defaultdict(lambda: defaultdict(int))
    total = 0

    grid_ll_cache, grid_dist_cache = {}, {}

    for raw in text_stream:   # raw is already str (TextIOWrapper)
        line = (raw or "").strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 3 or not TS_RE.match(parts[0]):
            continue

        # frequency
        try:
            f = float(parts[1])           # may be kHz or MHz
            freq_mhz = f / 1000.0 if f > 1000 else f
        except Exception:
            continue

        if "CQ" not in parts:
            continue

        band = band_from_freq_mhz(freq_mhz)
        # find last grid-like token
        grid = ""
        for tok in reversed(parts):
            if looks_like_grid(tok):
                grid = tok.upper()
                break

        total += 1
        per_band[band] += 1

        if grid:
            dist = grid_dist_cache.get(grid)
            if dist is None:
                ll = grid_ll_cache.get(grid)
                if ll is None:
                    try: ll = maidenhead_to_latlon(grid)
                    except Exception: ll = None
                    grid_ll_cache[grid] = ll
                if ll:
                    dist = haversine_km(my[0], my[1], ll[0], ll[1])
                    grid_dist_cache[grid] = dist

            if dist:
                bucket = int(dist // bin_km) * bin_km
                dist_bins[bucket] += 1
                dist_bins_by_band[band][bucket] += 1

    return {
        "source": "FT8 ALL.TXT",
        "total_spots": total,
        "bands": dict(per_band),
        "distance_histogram": {str(k): v for k, v in sorted(dist_bins.items())},
        "distance_histograms_by_band": {
            b: {str(k): v for k, v in sorted(bins.items())}
            for b, bins in dist_bins_by_band.items()
        },
    }

