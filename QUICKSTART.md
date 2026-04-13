# Quick Start Guide

## Prerequisites

- Python 3.8+
- pip (package installer)
- 8GB RAM (GPU recommended for faster inference)

## Installation (5 minutes)

### 1. Navigate to project directory
```bash
cd gan_api
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create weights directory (optional - model will initialize with random weights if missing)
```bash
mkdir -p weights
```

## Running the API

### Development Mode (with auto-reload)
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### With Gunicorn (Multi-worker)
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

The API will be available at `http://localhost:8000`

## First Test

### 1. Check Health
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
  --output my_image.jpg
```

This will create `my_image.jpg` in your current directory!

### 3. View API Documentation
Open your browser and go to: `http://localhost:8000/docs`

## Using the Python Client

```python
import requests

# Generate image
response = requests.post(
    "http://localhost:8000/api/v1/generate",
    json={"prompt": "A futuristic city with flying cars"}
)

# Save image
with open("generated.jpg", "wb") as f:
    f.write(response.content)
```

Or use the provided client script:

```bash
# Modify client_example.py with your prompts
python client_example.py
```

## Docker Deployment (Optional)

### Build image
```bash
docker build -t gan-backend .
```

### Run container
```bash
docker run --gpus all -p 8000:8000 gan-backend
```

### Using Docker Compose
```bash
docker-compose up -d
```

## Troubleshooting

### Issue: "CUDA out of memory"
**Solution:**
```bash
# Use CPU instead
DEVICE=cpu uvicorn app.main:app --port 8000
```

### Issue: "Model weights not found"
**Solution:** The model will work with random initialization. To use pre-trained weights:
```python
from app.models.generator import Generator

# Create and train a model, then save it
generator = Generator()
generator.save_weights("weights/generator.pth")
```

### Issue: Slow inference (>30 seconds)
**Solution:** You're probably using CPU. Use GPU for better performance:
```bash
# Verify CUDA is available
python -c "import torch; print(torch.cuda.is_available())"

# If True, CUDA will be used automatically
```

### Issue: "Port 8000 already in use"
**Solution:** Use a different port
```bash
uvicorn app.main:app --port 8001
```

## Key Files

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI application entry point |
| `app/api/routes.py` | API endpoints |
| `app/services/inference.py` | Image generation logic |
| `app/models/generator.py` | Generator model architecture |
| `requirements.txt` | Python dependencies |
| `README.md` | Full documentation |
| `ARCHITECTURE.md` | System design details |

## Next Steps

1. **Customize Model**: Edit `app/models/generator.py` to change architecture
2. **Add Authentication**: Implement JWT in `app/api/routes.py`
3. **Deploy**: Use Docker/Kubernetes for production
4. **Tune Performance**: Adjust batch size, model size, etc.

## API Endpoints Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | API information |
| GET | `/api/v1/health` | Check if API is running |
| POST | `/api/v1/generate` | Generate image from text |

## Request/Response Examples

### Request
```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A cozy cabin in the snow with warm lights",
    "seed": 42,
    "guidance_scale": 1.0
  }'
```

### Response
- Status: 200 OK
- Content-Type: image/jpeg
- Body: Raw JPEG image bytes

## Performance Tips

1. **Use GPU**: 3-5x faster than CPU
2. **Lower Image Quality**: Reduce `IMAGE_SIZE` to 128 for faster generation
3. **Batch Requests**: Process multiple users with multi-worker setup
4. **Cache CLIP Embeddings**: For repeated prompts, cache the embeddings

## Getting Help

- See `README.md` for detailed documentation
- Check `ARCHITECTURE.md` for technical details
- Run `pytest` to verify installation: `pytest tests/`
- Check FastAPI docs: http://localhost:8000/docs

---

**Happy generating! 🎨**
