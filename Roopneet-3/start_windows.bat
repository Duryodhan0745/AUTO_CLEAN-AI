@echo off
echo.
echo ==============================================
echo           AutoPrep AI  v1.0
echo    ML Data Preprocessing Engine
echo ==============================================
echo.

cd /d "%~dp0"

echo [1/2] Installing/Checking Python dependencies...
python -m pip install -r requirements.txt --quiet
echo.

echo [2/2] Starting FastAPI backend on http://localhost:8000
echo.
echo Frontend: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.

python main.py
echo.
echo Press Ctrl+C to stop.
echo.

python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
