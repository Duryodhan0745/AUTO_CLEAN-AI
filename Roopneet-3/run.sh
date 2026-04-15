#!/bin/bash
# AutoPrep AI - Start Script

set -e

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║          AutoPrep AI  v1.0               ║"
echo "║   ML Data Preprocessing Engine           ║"
echo "╚══════════════════════════════════════════╝"
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "📦 Installing Python dependencies..."
pip install -r "$SCRIPT_DIR/requirements.txt" --quiet

echo ""
echo "🚀 Starting FastAPI backend on http://localhost:8000"
echo "🌐 Frontend: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""

cd "$SCRIPT_DIR"
python main.py
echo ""
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop."
echo ""

cd "$SCRIPT_DIR/backend"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
