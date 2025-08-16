# backend/main.py
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from . import parser
import io

app = FastAPI(title="Propagation Analyzer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/analyze")
async def analyze(
    locator: str = Form(...),
    bin_km: int = Form(1000),
    file: UploadFile = File(...),
):
    if not locator or len(locator.strip()) < 4:
        raise HTTPException(400, detail="Locator must be at least 4 characters (e.g., KP26).")

    # Peek a small header to detect format, then rewind
    head_bytes = await file.read(4096)
    await file.seek(0)
    head = head_bytes.decode("utf-8", errors="ignore")
    first = (head.splitlines() or [""])[0].strip().lower()

    # CSV heuristics: header containing band/; or band, or any header line with separators
    looks_csv = (
        ("band" in first and (";" in first or "," in first))
        or ("qso_date" in first)
        or ("gridsquare" in first)
        or ("freq" in first and (";" in first or "," in first))
    )

    stream = io.TextIOWrapper(file.file, encoding="utf-8", errors="ignore", newline="")

    try:
        if looks_csv:
            return parser.analyze_csv_stream(stream, locator.strip(), int(bin_km))
        else:
            return parser.analyze_alltxt_stream(stream, locator.strip(), int(bin_km))
    except Exception as e:
        raise HTTPException(400, detail=f"Parse error: {e}")

