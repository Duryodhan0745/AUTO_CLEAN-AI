import uuid
import os
import json
from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

from ingestion import load_csv
from profiling import profile_dataset
from execution_engine import run_pipeline
from pipeline_builder import build_pipeline_script

try:
    from ydata_profiling import ProfileReport
    YDATA_AVAILABLE = True
except ImportError:
    YDATA_AVAILABLE = False

app = FastAPI(title="AutoPrep AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create storage directories in the project root
APP_DIR = os.path.dirname(__file__)
DATASETS_DIR = os.path.join(APP_DIR, "storage", "datasets")
PIPELINES_DIR = os.path.join(APP_DIR, "storage", "pipelines")
os.makedirs(DATASETS_DIR, exist_ok=True)
os.makedirs(PIPELINES_DIR, exist_ok=True)

print(f"📁 Storage directories ready:")
print(f"   Datasets: {DATASETS_DIR}")
print(f"   Pipelines: {PIPELINES_DIR}")

metadata_store = {}

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="File is empty.")
    dataset_id = str(uuid.uuid4())
    
    # Get file extension and save with original extension
    _, file_ext = os.path.splitext(file.filename or "file.csv")
    raw_path = os.path.join(DATASETS_DIR, f"{dataset_id}_raw{file_ext}")
    
    with open(raw_path, "wb") as f:
        f.write(contents)
    try:
        df = load_csv(raw_path)
    except Exception as e:
        os.remove(raw_path)
        raise HTTPException(status_code=400, detail=f"Invalid file: {str(e)}")
    metadata_store[dataset_id] = {
        "filename": file.filename,
        "raw_path": raw_path,
        "shape": df.shape,
    }
    return {"dataset_id": dataset_id, "filename": file.filename, "rows": df.shape[0], "columns": df.shape[1]}

@app.get("/profile/{dataset_id}")
def get_profile(dataset_id: str):
    if dataset_id not in metadata_store:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    raw_path = metadata_store[dataset_id]["raw_path"]
    df = load_csv(raw_path)
    profile = profile_dataset(df)
    return JSONResponse(content=profile)

@app.post("/process/{dataset_id}")
def process_dataset(dataset_id: str, config: dict = Body(...)):
    if dataset_id not in metadata_store:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    raw_path = metadata_store[dataset_id]["raw_path"]
    try:
        df = load_csv(raw_path)
    except Exception as e:
        print(f"Error loading CSV: {e}")
        raise HTTPException(status_code=400, detail=f"Error loading file: {str(e)}")
    
    try:
        print(f"Config received: {config}")
        cleaned_df, logs = run_pipeline(df, config)
        print(f"Pipeline completed successfully")
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Pipeline failed: {error_details}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
    
    try:
        cleaned_path = os.path.join(DATASETS_DIR, f"{dataset_id}_cleaned.csv")
        cleaned_df.to_csv(cleaned_path, index=False, encoding="utf-8")
        pipeline_script = build_pipeline_script(config, logs)
        pipeline_path = os.path.join(PIPELINES_DIR, f"{dataset_id}_pipeline.py")
        with open(pipeline_path, "w", encoding="utf-8") as f:
            f.write(pipeline_script)
        metadata_store[dataset_id]["cleaned_path"] = cleaned_path
        metadata_store[dataset_id]["pipeline_path"] = pipeline_path
        metadata_store[dataset_id]["logs"] = logs
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error saving results: {error_details}")
        raise HTTPException(status_code=500, detail=f"Error saving results: {str(e)}")

    report_path = None
    if YDATA_AVAILABLE:
        try:
            report_path = os.path.join(PIPELINES_DIR, f"{dataset_id}_report.html")
            profile = ProfileReport(
                cleaned_df,
                title="AutoPrep AI — Cleaned Dataset Report",
                explorative=True,
                minimal=False,
            )
            profile.to_file(report_path)
            metadata_store[dataset_id]["report_path"] = report_path
        except Exception:
            report_path = None

    return {
        "status": "success",
        "rows_before": df.shape[0],
        "cols_before": df.shape[1],
        "rows_after": cleaned_df.shape[0],
        "cols_after": cleaned_df.shape[1],
        "logs": logs,
        "report_available": report_path is not None,
    }

@app.get("/report/{dataset_id}", response_class=HTMLResponse)
def get_report(dataset_id: str):
    meta = metadata_store.get(dataset_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    if not YDATA_AVAILABLE:
        raise HTTPException(status_code=503, detail="ydata-profiling is not installed.")
    report_path = meta.get("report_path")
    if not report_path or not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="Report not generated yet. Run /process first.")
    with open(report_path, "r", encoding="utf-8") as f:
        html = f.read()
    return HTMLResponse(content=html)

@app.get("/download-report/{dataset_id}")
def download_report(dataset_id: str):
    meta = metadata_store.get(dataset_id)
    if not meta or "report_path" not in meta:
        raise HTTPException(status_code=404, detail="Report not found.")
    return FileResponse(meta["report_path"], filename="profiling_report.html", media_type="text/html")

@app.get("/download/{dataset_id}")
def download_csv(dataset_id: str):
    meta = metadata_store.get(dataset_id)
    if not meta or "cleaned_path" not in meta:
        raise HTTPException(status_code=404, detail="Cleaned dataset not found.")
    return FileResponse(meta["cleaned_path"], filename="cleaned_dataset.csv", media_type="text/csv")

@app.get("/download-pipeline/{dataset_id}")
def download_pipeline(dataset_id: str):
    meta = metadata_store.get(dataset_id)
    if not meta or "pipeline_path" not in meta:
        raise HTTPException(status_code=404, detail="Pipeline script not found.")
    return FileResponse(meta["pipeline_path"], filename="pipeline.py", media_type="text/plain")

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    try:
        FRONTEND_DIR = os.path.join(os.path.dirname(__file__))
        index_path = os.path.join(FRONTEND_DIR, "index.html")
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return "<h1>AutoPrep AI Backend</h1><p>API running at <a href='/docs'>/docs</a></p>"

@app.get("/styles.css", response_class=FileResponse)
def serve_css():
    try:
        FRONTEND_DIR = os.path.join(os.path.dirname(__file__))
        css_path = os.path.join(FRONTEND_DIR, "styles.css")
        return FileResponse(css_path, media_type="text/css")
    except Exception:
        return "/* CSS file not found */"

@app.get("/api.js", response_class=FileResponse)
def serve_api_js():
    try:
        FRONTEND_DIR = os.path.join(os.path.dirname(__file__))
        js_path = os.path.join(FRONTEND_DIR, "api.js")
        return FileResponse(js_path, media_type="text/javascript")
    except Exception:
        return "// JS file not found"

@app.get("/app.js", response_class=FileResponse)
def serve_app_js():
    try:
        FRONTEND_DIR = os.path.join(os.path.dirname(__file__))
        js_path = os.path.join(FRONTEND_DIR, "app.js")
        return FileResponse(js_path, media_type="text/javascript")
    except Exception:
        return "// JS file not found"

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*50)
    print("   AutoPrep AI - ML Data Preprocessing Engine")
    print("="*50)
    print("\n🚀 Starting FastAPI server on http://localhost:8000")
    print("🌐 Open frontend: http://localhost:8000")
    print("📚 API docs: http://localhost:8000/docs")
    print("\nCtrl+C to stop\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
