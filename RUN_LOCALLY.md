# How to Run Locally

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- 8GB RAM (GPU recommended for faster inference)
- CUDA toolkit (optional, for GPU support)

## Step-by-Step Setup

### 1. Navigate to Project Directory

```bash
cd /home/kaustubh/Downloads/gan_api
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
# On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

This will install:
- FastAPI (web framework)
- Uvicorn (ASGI server)
- PyTorch (deep learning)
- Transformers (CLIP model)
- Pydantic (validation)
- Pillow (image processing)
- And more...

### 4. Verify Installation

```bash
# Check if imports work
python3 -c "
from app.core.config import settings
from app.models.generator import Generator
from app.services.inference import InferenceService
print('✅ All imports successful!')
print(f'Device: {settings.DEVICE}')
"
```

## Running the Server

### Option 1: Development Mode (with auto-reload)

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started server process [12345]
```

### Option 2: Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Option 3: Using Gunicorn (Multiple Workers)

```bash
# Install gunicorn if not already installed
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

## Testing the API

Once the server is running, open a new terminal:

### 1. Check Health Status

```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 2. Generate an Image

```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A beautiful sunset over the ocean"}' \
  --output generated_image.jpg
```

This will create `generated_image.jpg` in your current directory!

### 3. View API Documentation

Open your browser and visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Using Python Client

Create a new Python file `test_local.py`:

```python
import requests
from pathlib import Path

def test_api():
    # Test health
    print("Testing health endpoint...")
    health_response = requests.get("http://localhost:8000/api/v1/health")
    print(f"Health: {health_response.json()}")
    
    # Generate image
    print("\nGenerating image...")
    response = requests.post(
        "http://localhost:8000/api/v1/generate",
        json={
            "prompt": "A beautiful sunset over mountains",
            "seed": 42,
            "guidance_scale": 1.0
        }
    )
    
    if response.status_code == 200:
        Path("test_image.jpg").write_bytes(response.content)
        print("✅ Image generated and saved as test_image.jpg!")
    else:
        print(f"❌ Error: {response.json()}")

if __name__ == "__main__":
    test_api()
```

Run it:
```bash
python test_local.py
```

## Using Docker (Optional)

### Build Docker Image

```bash
docker build -t gan-backend:latest .
```

### Run with Docker

```bash
docker run -p 8000:8000 gan-backend:latest
```

### Run with Docker Compose

```bash
docker-compose up
```

## Troubleshooting

### Issue: ModuleNotFoundError: No module named 'torch'

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Port 8000 Already in Use

**Solution:**
```bash
# Use a different port
uvicorn app.main:app --port 8001
```

Or kill the process using port 8000:
```bash
# On Linux/Mac
lsof -ti:8000 | xargs kill -9

# On Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Issue: CUDA Out of Memory

**Solution:**
```bash
# Use CPU instead
DEVICE=cpu uvicorn app.main:app --port 8000
```

### Issue: Slow Inference (>30 seconds)

**Solution:**
```bash
# Check if CUDA is available
python3 -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

# If False, you're using CPU - use GPU for faster inference
```

### Issue: "Model weights not found" Warning

**Solution:**
The model will work with random initialization. If you have pre-trained weights, place them in:
```
weights/generator.pth
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
DEBUG=False
DEVICE=cuda
CLIP_MODEL_NAME=openai/clip-vit-base-patch32
IMAGE_SIZE=256
JPEG_QUALITY=95
```

Then run:
```bash
# Load from .env and run
set -a && source .env && set +a
uvicorn app.main:app --port 8000
```

## Testing the Full API

### Using the provided client example:

```bash
python client_example.py
```

This will generate multiple images with different prompts and save them locally.

## Performance Tips

### For Faster Generation
1. Use GPU (CUDA) - 3-5x faster than CPU
2. Use simpler prompts
3. Lower resolution (reduce IMAGE_SIZE if needed)

### For Better Quality
1. Increase JPEG_QUALITY to 100
2. Use more complex prompts
3. Experiment with different seeds

## Common Endpoints Summary

| Method | URL | Purpose |
|--------|-----|---------|
| GET | `http://localhost:8000/api/v1/health` | Check API status |
| POST | `http://localhost:8000/api/v1/generate` | Generate image from text |
| GET | `http://localhost:8000/docs` | API documentation |
| GET | `http://localhost:8000/` | API info |

## Stopping the Server

Press `CTRL+C` in the terminal running the server:

```
^C (KeyboardInterrupt)
INFO:     Shutting down
INFO:     Waiting for application shutdown.
```

## Next Steps

1. ✅ Set up and run locally
2. Generate a few test images
3. Try the interactive API docs at `/docs`
4. Experiment with different prompts
5. Check out DEPLOYMENT.md for production setup
6. Read ARCHITECTURE.md for technical details

## Help & Support

- **View full README**: See `README.md`
- **API Reference**: See `API_REFERENCE.md`
- **Architecture**: See `ARCHITECTURE.md`
- **Deployment**: See `DEPLOYMENT.md`

---

**Happy generating! 🎨**
