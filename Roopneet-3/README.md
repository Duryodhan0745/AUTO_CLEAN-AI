# AutoPrep AI

A production-grade CSV preprocessing engine that converts raw data into clean, ML-ready datasets with full transparency and a reproducible pipeline export.

---

## Folder Structure

```
autoprep/
├── run.sh                          # One-command startup (Linux/Mac)
├── start_windows.bat               # One-command startup (Windows)
├── frontend/
│   ├── index.html                  # Full SPA (upload → dashboard → results)
│   ├── css/
│   │   └── styles.css
│   └── js/
│       ├── api.js                  # API client
│       └── app.js                  # App logic & UI
├── backend/
│   ├── main.py                     # FastAPI app + all endpoints
│   ├── requirements.txt
│   └── modules/
│       ├── __init__.py
│       ├── ingestion.py            # CSV loading & validation
│       ├── profiling.py            # Dataset analysis
│       ├── column_removal.py       # Drop user-selected columns
│       ├── missing.py              # Missing value strategies
│       ├── outliers.py             # IQR-based outlier handling
│       ├── encoding.py             # One-hot / Label encoding
│       ├── scaling.py              # Standard / MinMax / Robust
│       ├── vif.py                  # Variance Inflation Factor filter
│       ├── rfe.py                  # Recursive Feature Elimination
│       ├── pca.py                  # PCA dimensionality reduction
│       ├── execution_engine.py     # Orchestrates the full pipeline
│       └── pipeline_builder.py     # Generates reproducible pipeline.py
└── storage/
    ├── datasets/                   # Raw + cleaned CSVs stored here
    └── pipelines/                  # Generated pipeline scripts + reports
```

---

## How to Run

### Option A — Linux / Mac (one command)
```bash
bash run.sh
```

### Option B — Windows (one command)
Double-click `start_windows.bat` or run it from Command Prompt.

### Option C — Manual
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Then open `frontend/index.html` in your browser.

> **Important:** The frontend calls `http://localhost:8000`. Open `index.html`
> directly as a file (no server needed for frontend). CORS is fully enabled on the backend.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload` | Upload CSV → returns `dataset_id` |
| GET | `/profile/{id}` | Full dataset analysis |
| POST | `/process/{id}` | Run pipeline with config JSON |
| GET | `/download/{id}` | Download cleaned CSV |
| GET | `/download-pipeline/{id}` | Download Python pipeline script |
| GET | `/report/{id}` | View ydata-profiling HTML report |
| GET | `/download-report/{id}` | Download profiling report |

Interactive API docs: http://localhost:8000/docs

---

## Pipeline Configuration Schema

```json
{
  "remove_columns": ["col1", "col2"],
  "missing_global": "mean",
  "missing": {
    "age": "median",
    "category": "mode"
  },
  "outliers": { "strategy": "cap" },
  "encoding": { "strategy": "onehot" },
  "scaling": { "strategy": "standard" },
  "vif": { "enabled": true, "threshold": 10 },
  "rfe": { "enabled": true, "target": "label_col", "n_features": 10 },
  "pca": { "enabled": false, "variance": 0.95 }
}
```

### Options

| Step | Options |
|------|---------|
| Missing | `mean`, `median`, `mode`, `drop_rows`, `drop_column` |
| Outliers | `cap` (Winsorise), `remove`, `keep` |
| Encoding | `onehot`, `label` |
| Scaling | `standard`, `minmax`, `robust` |
| VIF | `enabled: true/false`, `threshold: float` |
| RFE | `enabled`, `target: column_name`, `n_features: int` |
| PCA | `enabled: true/false`, `variance: 0.95` |

---

## Bug Fixes Applied (v1.0 → v1.0.1)

1. **`index.html` script paths fixed** — Changed `css/styles.css`, `js/api.js`, `js/app.js`
   paths that were correct but the files didn't exist in those subfolders.
   Now the folder structure matches what `index.html` references.

2. **`modules/` package created properly** — All Python modules moved into
   `backend/modules/` with `__init__.py` so imports like
   `from modules.ingestion import load_csv` work correctly in `main.py`
   and `execution_engine.py`.

3. **Upload button `onclick` conflict removed** — The original `index.html`
   had `onclick="document.getElementById('file-input').click()"` hardcoded
   on the upload button, which bypassed `app.js`'s `handleFile()` logic.
   Now all event handling is done purely through `app.js` listeners.

4. **`__init__.py` repositioned** — Moved from the root directory into
   `backend/modules/` where Python needs it to recognize the package.

5. **VIF import made safe** — `vif.py` now catches `ImportError` for
   `statsmodels` gracefully instead of crashing the entire pipeline.

---

## Dependencies

- **FastAPI** — REST API framework
- **uvicorn** — ASGI server
- **pandas** — Data manipulation
- **numpy** — Numerical operations
- **scikit-learn** — Encoding, scaling, RFE, PCA
- **statsmodels** — VIF calculation
- **python-multipart** — File upload support
- **ydata-profiling** *(optional)* — Full HTML profiling report
