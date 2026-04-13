#!/bin/bash
# Startup script for GAN Backend API

set -e

echo "🚀 GAN Backend API Startup"
echo "================================"

# Check Python version
echo "✅ Checking Python version..."
python --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Create weights directory
echo "📁 Creating weights directory..."
mkdir -p weights

# Display API info
echo ""
echo "================================"
echo "✨ Setup Complete!"
echo "================================"
echo ""
echo "To start the API, run:"
echo ""
echo "  Option 1 (Development with auto-reload):"
echo "  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "  Option 2 (Production):"
echo "  uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4"
echo ""
echo "  Option 3 (With Gunicorn):"
echo "  gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app"
echo ""
echo "API Documentation: http://localhost:8000/docs"
echo "Health Check: http://localhost:8000/api/v1/health"
echo "Generate Image: POST http://localhost:8000/api/v1/generate"
echo ""
