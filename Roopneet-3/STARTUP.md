# AutoPrep AI - Getting Started

## Frontend-Backend Connection ✅

The frontend and backend are now fully integrated:

### Architecture
```
Frontend (HTML/CSS/JS)
    ↓ HTTP Requests
Backend (FastAPI)
    ↓ Processes CSV
Python Modules (ingestion, profiling, execution, etc.)
```

### File Structure
```
Roopneet-3/
├── index.html              # Frontend UI
├── styles.css              # CSS styling  
├── api.js                  # API client (declares endpoints)
├── app.js                  # Frontend logic
├── main.py                 # FastAPI backend (serves frontend + APIs)
├── requirements.txt        # Python dependencies
├── start_windows.bat       # Windows startup script
├── run.sh                  # Linux/Mac startup script
└── *.py modules           # Data processing modules
```

---

## How to Run

### Windows
```bash
# Method 1: Run the batch file (automated)
double-click start_windows.bat

# Method 2: Manual command
python main.py
```

### Linux / Mac
```bash
# Make script executable
chmod +x run.sh

# Run the script
./run.sh

# Or manually
python main.py
```

---

## What Happens on Startup

1. **Dependencies Installed**: `pip install -r requirements.txt`
2. **Backend Starts**: FastAPI server listening on `http://localhost:8000`
3. **Storage Created**: Directories for datasets and pipelines
4. **Frontend Served**: At `http://localhost:8000`

---

## Access Points

| URL | Purpose |
|-----|---------|
| `http://localhost:8000` | Frontend UI (AutoPrep AI) |
| `http://localhost:8000/docs` | API documentation (Swagger UI) |
| `http://localhost:8000/redoc` | API documentation (ReDoc) |

---

## Frontend-Backend API Connections

The frontend (`api.js`) connects to:

### Upload & Profiling
- **POST** `/upload` - Upload CSV file
- **GET** `/profile/{dataset_id}` - Analyze uploaded dataset

### Processing
- **POST** `/process/{dataset_id}` - Run preprocessing pipeline with config

### Download Results
- **GET** `/download/{dataset_id}` - Download cleaned CSV
- **GET** `/download-pipeline/{dataset_id}` - Download Python pipeline script
- **GET** `/report/{dataset_id}` - View profiling report
- **GET** `/download-report/{dataset_id}` - Download profiling report

---

## Processing Pipeline

When you run the pipeline, the backend processes your data through:

1. **Column Removal** - Remove selected columns
2. **Missing Values** - Handle NaN/null values (mean, median, mode, etc.)
3. **Outliers** - Detect and handle outliers (cap, remove, or keep)
4. **Encoding** - Convert categorical to numeric (One-Hot or Label)
5. **Scaling** - Normalize numeric features (Standard, Min-Max, Robust)
6. **VIF Filter** - Remove multicollinearity (Variance Inflation Factor)
7. **RFE** - Feature selection using Recursive Feature Elimination
8. **PCA** - Dimensionality reduction (95% variance)

---

## Example Workflow

1. **Open** `http://localhost:8000` in browser
2. **Upload** your CSV file (drag & drop or click)
3. **View** dataset profile and statistics
4. **Configure** pipeline settings or use Auto mode
5. **Run** pipeline
6. **Download** cleaned dataset and Python script

---

## Troubleshooting

### Port 8000 Already in Use
```bash
# Windows: Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID)
taskkill /PID <PID> /F
```

### Python Module Import Errors
Ensure all `.py` files are in the same directory as `main.py`.

### Dependencies Not Installing
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Then install requirements
pip install -r requirements.txt
```

### Static Files Not Serving
The frontend (HTML/CSS/JS) is now automatically served by the FastAPI backend. Files must be in the same directory as `main.py`.

---

## Tear Down

Stop the backend server by pressing `Ctrl+C` in the terminal.

---

**Version**: 1.0  
**Status**: ✅ Frontend-Backend Connected and Ready
