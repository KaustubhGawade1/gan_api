# GAN Backend API

Production-ready FastAPI backend for serving conditional GAN models with CLIP-based text embeddings.

## Features

- ✅ **Text-to-Image Generation**: Convert text prompts to images using conditional GAN
- ✅ **CLIP Integration**: Leverage OpenAI's CLIP for semantic text embeddings
- ✅ **Production-Ready**: Modular architecture with dependency injection
- ✅ **Singleton Pattern**: Load models only once for efficiency
- ✅ **Streaming Responses**: Raw JPEG bytes (not base64)
- ✅ **CUDA Support**: Automatic GPU detection and utilization
- ✅ **Comprehensive Logging**: Built-in error handling and health checks
- ✅ **FastAPI Best Practices**: Type hints, validation, automatic documentation

## Project Structure

```
gan_api/
├── app/
│   ├── main.py                 # FastAPI application factory
│   ├── api/
│   │   └── routes.py           # API endpoints
│   ├── core/
│   │   ├── config.py           # Configuration management
│   │   └── dependencies.py     # Dependency injection (singleton models)
│   ├── models/
│   │   └── generator.py        # PyTorch Generator model
│   ├── services/
│   │   └── inference.py        # Inference service with CLIP
│   ├── schemas/
│   │   └── request.py          # Pydantic models for validation
│   └── utils/
│       └── image.py            # Image processing utilities
├── weights/
│   └── generator.pth           # Pre-trained model weights
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
└── README.md
```

## Installation

### Prerequisites

- Python 3.8+
- CUDA 11.8+ (optional, for GPU support)
- 8GB RAM minimum

### Setup

1. Clone the repository:
```bash
cd gan_api
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment (optional):
```bash
cp .env.example .env
# Edit .env as needed
```

## Running the API

### Development

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Production

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### With Gunicorn (Production)

```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

## API Documentation

Once running, visit:
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Endpoints

### Health Check

```bash
curl http://localhost:8000/api/v1/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### Generate Image

```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A beautiful sunset over the ocean with mountains",
    "seed": 42,
    "guidance_scale": 1.0
  }' \
  --output generated_image.jpg
```

**Request Schema:**

```json
{
  "prompt": "string (required, 1-500 chars)",
  "seed": "integer (optional, default: 42)",
  "guidance_scale": "float (optional, default: 1.0)"
}
```

**Response:**
- Raw JPEG bytes (Content-Type: image/jpeg)
- Status: 200 OK on success
- Status: 400 Bad Request if validation fails
- Status: 500 Internal Server Error if generation fails

## Configuration

Edit `.env` or environment variables:

```env
# Debug mode
DEBUG=False

# API settings
API_PREFIX=/api/v1
HOST=0.0.0.0
PORT=8000

# Model settings
MODEL_WEIGHTS_PATH=./weights/generator.pth
DEVICE=cuda  # or 'cpu'
CLIP_MODEL_NAME=openai/clip-vit-base-patch32

# Generation settings
IMAGE_SIZE=256
JPEG_QUALITY=95
```

## Architecture

### Model Manager (Singleton Pattern)

The `ModelManager` ensures models are loaded only once:

```python
# Models are loaded during app startup
model_manager = ModelManager()
model_manager.initialize()  # Called once in lifespan

# Get inference service on every request
inference_service = model_manager.get_inference_service()
```

### Inference Pipeline

1. **Text Encoding**: Prompt → CLIP → Embedding (512-dim)
2. **Noise Generation**: Random vector (100-dim)
3. **Generator Forward**: [Embedding, Noise] → Image (256x256x3)
4. **Denormalization**: [-1, 1] → [0, 255]
5. **Image Encoding**: Tensor → PIL → JPEG bytes

### Model Details

**Generator Architecture:**
- Input: Noise (100-dim) + Text Embedding (512-dim)
- Architecture: Dense → Reshape → 6x Transposed Convolution
- Output: Image (3, 256, 256) in [-1, 1]

**CLIP Model:**
- Model: openai/clip-vit-base-patch32
- Output: Text embeddings (512-dim)
- Normalized using L2 norm

## Performance Notes

- **Time per Request**: ~2-5 seconds (GPU), ~15-30 seconds (CPU)
- **Memory Usage**: ~4GB (GPU), ~2GB (CPU)
- **Batch Size**: Currently 1 (single prompt per request)
- **Concurrency**: Safe for multiple concurrent requests

## Error Handling

### 400 Bad Request
```json
{
  "detail": "Prompt cannot be empty"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Generation error: CUDA out of memory"
}
```

## Development

### Run Tests

```bash
pytest
```

### Code Style

```bash
black app/
flake8 app/
mypy app/
```

### Generate Model Weights

If `weights/generator.pth` doesn't exist, the model will initialize with random weights. To train a proper model:

```python
from app.models.generator import Generator

# Create and train model
generator = Generator()
# ... training code ...
generator.save_weights("weights/generator.pth")
```

## Troubleshooting

### CUDA Out of Memory
- Reduce IMAGE_SIZE to 128 or 64
- Use CPU device: `DEVICE=cpu`

### Slow Inference
- Use CUDA if available
- Run uvicorn with: `--workers 1 --cores 4`

### Models Not Loaded
- Check logs during startup
- Verify weights file exists
- Check disk space (transformers cache)

## Security Considerations

### For Production:

1. **CORS**: Update to specific origins
```python
allow_origins=["https://yourdomain.com"]
```

2. **Rate Limiting**: Add rate limit middleware
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
```

3. **Authentication**: Add JWT token validation
```python
from fastapi.security import HTTPBearer
security = HTTPBearer()
```

4. **Request Size**: Limit prompt size (already done: max 500 chars)

5. **Timeout**: Add timeout for long-running requests
```python
@app.post("/generate")
async def generate_image(...):
    async with asyncio.timeout(60):
        # Generate image
```

## Performance Optimization

### Multi-Worker Deployment

**With Gunicorn + Uvicorn:**
```bash
gunicorn -w 2 -k uvicorn.workers.UvicornWorker app.main:app
```

**With Docker:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app /app/app
CMD ["gunicorn", "-w", "2", "-k", "uvicorn.workers.UvicornWorker", "app.main:app"]
```

### Caching

For repeated prompts, consider caching:
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def encode_text(prompt: str):
    return inference_service.encode_text(prompt)
```

## License

MIT

## Support

For issues or questions, please check the FastAPI documentation:
- https://fastapi.tiangolo.com/
- https://pytorch.org/
- https://huggingface.co/
# gan_api
