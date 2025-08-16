from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import parser

app = FastAPI()

# Allow frontend (localhost:5173) to talk with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze_file(
    own_locator: str = Form(...),
    bin_km: int = Form(1000),
    show_hours: bool = Form(True),
    show_polar: bool = Form(True),
    file: UploadFile = File(...)
):
    """Receive uploaded file + config, return JSON with analysis."""
    content = await file.read()
    results = parser.analyze(content.decode("utf-8", errors="ignore"),
                             own_locator, bin_km, show_hours, show_polar)
    return results

