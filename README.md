# Propagation Analyzer

Simple web app to analyze amateur radio logs.  
Supports WSJT-X `ALL.TXT` and Log4OM `CSV`.

## What it shows
- Band distribution (pie chart)
- Distance histogram (all spots)
- Per-band distance histograms

## Run locally (production style)

Backend serves the built frontend.

1) Build frontend

cd frontend
npm install
npm run build

2) Start backend

cd ../backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000


Open `http://<server>:8000/`

## Development (hot reload)

Frontend (Vite):

cd frontend
npm install
npm run dev


Backend:

cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload


## Usage
1. Open the page.
2. Enter your locator (e.g. KP26vl).
3. Pick distance bin (e.g. 1000 km).
4. Upload `ALL.TXT` or `CSV`.
5. Click “Upload & Analyze”.

Large ALL.TXT files (100+ MB) are supported.

## Notes
- API endpoint: `POST /api/analyze` (multipart form: `locator`, `bin_km`, `file`)
- Frontend static files are served by FastAPI from `frontend/dist`.
